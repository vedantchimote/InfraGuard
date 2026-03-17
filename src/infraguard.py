"""
InfraGuard main application orchestrator.

This module coordinates all components for continuous metrics collection,
anomaly detection, and alerting.
"""

import signal
import sys
import time
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from src.config.configuration_manager import ConfigurationManager, ConfigurationError
from src.collector.prometheus_collector import PrometheusCollector
from src.collector.data_formatter import DataFormatter
from src.ml.isolation_forest_detector import IsolationForestDetector
from src.ml.forecaster import TimeSeriesForecaster
from src.alerter.alert_manager import AlertManager
from src.utils.logging_config import setup_logging
from src.health_server import HealthServer


logger = logging.getLogger(__name__)


class InfraGuard:
    """
    Main InfraGuard application orchestrator.
    
    Coordinates metrics collection, anomaly detection, and alerting
    in a continuous loop with configurable intervals.
    
    Attributes:
        config_mgr: ConfigurationManager instance
        collector: PrometheusCollector instance
        formatter: DataFormatter instance
        detector: IsolationForestDetector instance
        forecaster: TimeSeriesForecaster instance (optional)
        alert_manager: AlertManager instance
        collection_interval: Seconds between collection cycles
        forecasting_enabled: Whether time-series forecasting is enabled
        running: Flag indicating if application is running
    
    Example:
        >>> app = InfraGuard('config/settings.yaml')
        >>> app.run()
    """
    
    def __init__(self, config_path: str):
        """
        Initialize InfraGuard application.
        
        Args:
            config_path: Path to configuration file
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        logger.info("=" * 60)
        logger.info("Initializing InfraGuard AIOps")
        logger.info("=" * 60)
        
        # Load configuration
        self.config_mgr = ConfigurationManager(config_path)
        
        # Setup logging from config
        self._setup_logging()
        
        # Initialize components
        logger.info("Initializing components...")
        
        # Prometheus collector
        prometheus_config = self.config_mgr.get_prometheus_config()
        self.collector = PrometheusCollector(prometheus_config)
        
        # Data formatter
        self.formatter = DataFormatter()
        
        # ML detector
        ml_config = self.config_mgr.get_ml_config()
        if_config = ml_config.get('isolation_forest', {})
        self.detector = IsolationForestDetector(if_config)
        
        # Load pre-trained model
        model_path = ml_config.get('model_path', 'models/pretrained/isolation_forest.pkl')
        self._load_model(model_path)
        
        # Time-series forecaster (optional)
        forecasting_config = self.config_mgr.get('forecasting', {})
        self.forecasting_enabled = forecasting_config.get('enabled', False)
        
        if self.forecasting_enabled:
            logger.info("Time-series forecasting is enabled")
            self.forecaster = TimeSeriesForecaster(forecasting_config)
            self.forecast_interval = forecasting_config.get('forecast_interval', 300)
            self.last_forecast_time: Optional[datetime] = None
        else:
            logger.info("Time-series forecasting is disabled")
            self.forecaster = None
            self.forecast_interval = None
            self.last_forecast_time = None
        
        # Alert manager
        alerting_config = self.config_mgr.get_alerting_config()
        self.alert_manager = AlertManager(alerting_config)
        
        # Collection settings
        collection_config = self.config_mgr.get_collection_config()
        self.collection_interval = collection_config.get('interval', 60)
        
        # Runtime state
        self.running = False
        self.last_collection_time: Optional[datetime] = None
        
        # Health server
        health_config = self.config_mgr.get('health', {})
        if health_config.get('enabled', True):
            health_port = health_config.get('port', 8000)
            self.health_server = HealthServer(health_port, self.get_status)
        else:
            self.health_server = None
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
        
        logger.info("InfraGuard initialization complete")
        logger.info(f"Collection interval: {self.collection_interval} seconds")
    
    def _setup_logging(self) -> None:
        """Configure logging from configuration."""
        logging_config = self.config_mgr.get_logging_config()
        
        log_level = logging_config.get('level', 'INFO')
        log_format = logging_config.get('format')
        log_file = logging_config.get('file')
        max_bytes = logging_config.get('max_bytes', 10485760)
        backup_count = logging_config.get('backup_count', 5)
        
        setup_logging(
            log_level=log_level,
            log_format=log_format,
            log_file=log_file,
            max_bytes=max_bytes,
            backup_count=backup_count
        )
    
    def _load_model(self, model_path: str) -> None:
        """
        Load pre-trained model at startup.
        
        Args:
            model_path: Path to model file
        """
        if Path(model_path).exists():
            try:
                logger.info(f"Loading pre-trained model from {model_path}")
                self.detector.load_model(model_path)
                logger.info("Model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                logger.warning("Application will start without pre-trained model")
        else:
            logger.warning(f"Model file not found: {model_path}")
            logger.warning("Run training script first: python scripts/train_model.py")
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.stop()
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    def _execute_collection_cycle(self) -> None:
        """
        Execute one collection, detection, and alerting cycle.
        
        This method:
        1. Collects metrics from Prometheus
        2. Formats data and adds features
        3. Detects anomalies using ML model
        4. Sends alerts for detected anomalies
        """
        try:
            logger.info("Starting collection cycle")
            cycle_start = time.time()
            
            # Collect metrics
            logger.debug("Collecting metrics from Prometheus")
            results = self.collector.collect_metrics()
            
            successful_results = [r for r in results if r['success']]
            if not successful_results:
                logger.warning("No metrics collected, skipping cycle")
                return
            
            logger.info(f"Collected {len(successful_results)} metric types")
            
            # Process each metric
            for result in successful_results:
                metric_name = result['query_name']
                metric_type = result['metric_type']
                
                try:
                    # Format data
                    df = self.formatter.format_prometheus_response(result['data'], metric_name)
                    
                    if df.empty:
                        logger.debug(f"No data for {metric_name}, skipping")
                        continue
                    
                    # Add features
                    rolling_windows = self.config_mgr.get('ml.rolling_windows', [5, 10, 30])
                    df = self.formatter.add_feature_columns(df, rolling_windows)
                    
                    # Detect anomalies
                    thresholds = self.config_mgr.get('ml.thresholds', {})
                    metric_threshold = thresholds.get(metric_type, {})
                    confidence_threshold = metric_threshold.get('confidence', 80)
                    
                    anomaly_results = self.detector.detect_anomalies(
                        df, metric_name, confidence_threshold
                    )
                    
                    # Process anomalies
                    anomalies = [r for r in anomaly_results if r.is_anomaly]
                    
                    if anomalies:
                        logger.info(f"Detected {len(anomalies)} anomalies in {metric_name}")
                        
                        # Determine severity based on confidence
                        for anomaly in anomalies:
                            severity = self._determine_severity(
                                anomaly.confidence,
                                metric_threshold
                            )
                            
                            logger.warning(
                                f"Anomaly in {metric_name}: "
                                f"value={anomaly.value:.2f}, "
                                f"confidence={anomaly.confidence:.1f}%, "
                                f"severity={severity}"
                            )
                            
                            # Send alert
                            self.alert_manager.send_alert(
                                metric_name=metric_name,
                                metric_value=anomaly.value,
                                confidence=anomaly.confidence,
                                severity=severity,
                                timestamp=anomaly.timestamp,
                                additional_context={
                                    'anomaly_score': anomaly.anomaly_score,
                                    'metric_type': metric_type
                                }
                            )
                    else:
                        logger.debug(f"No anomalies detected in {metric_name}")
                
                except Exception as e:
                    logger.error(f"Error processing {metric_name}: {e}", exc_info=True)
                    continue
            
            # Update last collection time
            self.last_collection_time = datetime.now()
            
            cycle_duration = time.time() - cycle_start
            logger.info(f"Collection cycle completed in {cycle_duration:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Collection cycle failed: {e}", exc_info=True)
    
    def _determine_severity(
        self,
        confidence: float,
        metric_threshold: dict
    ) -> str:
        """
        Determine severity level based on confidence.
        
        Args:
            confidence: Anomaly confidence percentage
            metric_threshold: Threshold configuration for metric
        
        Returns:
            Severity level ('high', 'medium', 'low')
        """
        high_threshold = metric_threshold.get('severity_high', 95)
        medium_threshold = metric_threshold.get('severity_medium', 85)
        
        if confidence >= high_threshold:
            return 'high'
        elif confidence >= medium_threshold:
            return 'medium'
        else:
            return 'low'
    
    def _execute_forecasting(self) -> None:
        """
        Execute time-series forecasting for predictive alerting.
        
        This method:
        1. Collects historical metrics from Prometheus
        2. Generates forecasts for the prediction window
        3. Checks for predicted threshold breaches
        4. Sends forecast alerts if breaches are predicted
        """
        if not self.forecasting_enabled or not self.forecaster:
            return
        
        # Check if it's time to run forecasting
        if self.last_forecast_time:
            time_since_last = (datetime.now() - self.last_forecast_time).total_seconds()
            if time_since_last < self.forecast_interval:
                return
        
        try:
            logger.info("Starting forecasting cycle")
            forecast_start = time.time()
            
            # Collect historical metrics (need more data for forecasting)
            # Query last 7 days of data
            logger.debug("Collecting historical metrics for forecasting")
            results = self.collector.collect_metrics()
            
            successful_results = [r for r in results if r['success']]
            if not successful_results:
                logger.warning("No metrics collected for forecasting, skipping")
                return
            
            logger.info(f"Collected {len(successful_results)} metric types for forecasting")
            
            # Process each metric
            for result in successful_results:
                metric_name = result['query_name']
                metric_type = result['metric_type']
                
                try:
                    # Format data
                    df = self.formatter.format_prometheus_response(result['data'], metric_name)
                    
                    if df.empty or len(df) < 2880:  # Need at least 2 days
                        logger.debug(
                            f"Insufficient data for forecasting {metric_name} "
                            f"({len(df)} points, need >= 2880)"
                        )
                        continue
                    
                    # Generate forecast
                    forecast_result = self.forecaster.forecast(df, metric_type)
                    
                    # Check for predicted breach
                    if forecast_result.breach_time:
                        logger.warning(
                            f"Threshold breach predicted for {metric_name} at "
                            f"{forecast_result.breach_time}: "
                            f"value={forecast_result.breach_value:.2f}"
                        )
                        
                        # Determine severity based on confidence interval
                        thresholds = self.config_mgr.get('ml.thresholds', {})
                        metric_threshold = thresholds.get(metric_type, {})
                        
                        # Use high severity for predicted breaches
                        severity = 'high'
                        
                        # Send forecast alert
                        self.alert_manager.send_forecast_alert(
                            metric_name=metric_name,
                            predicted_value=forecast_result.breach_value,
                            breach_time=forecast_result.breach_time,
                            confidence_lower=forecast_result.confidence_interval_lower,
                            confidence_upper=forecast_result.confidence_interval_upper,
                            severity=severity,
                            prediction_window_minutes=self.forecaster.prediction_window_minutes,
                            additional_context={
                                'metric_type': metric_type
                            }
                        )
                    else:
                        logger.debug(f"No threshold breach predicted for {metric_name}")
                
                except ValueError as e:
                    logger.debug(f"Cannot forecast {metric_name}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error forecasting {metric_name}: {e}", exc_info=True)
                    continue
            
            # Update last forecast time
            self.last_forecast_time = datetime.now()
            
            forecast_duration = time.time() - forecast_start
            logger.info(f"Forecasting cycle completed in {forecast_duration:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Forecasting cycle failed: {e}", exc_info=True)
    
    def run(self) -> None:
        """
        Run main collection loop.
        
        Continuously collects metrics, detects anomalies, and sends alerts
        at configured intervals until stopped.
        """
        logger.info("=" * 60)
        logger.info("Starting InfraGuard AIOps")
        logger.info("=" * 60)
        
        # Start health server
        if self.health_server:
            self.health_server.start()
        
        self.running = True
        
        try:
            while self.running:
                try:
                    # Execute collection cycle
                    self._execute_collection_cycle()
                    
                    # Execute forecasting (if enabled and due)
                    if self.forecasting_enabled:
                        self._execute_forecasting()
                    
                    # Sleep until next collection
                    if self.running:
                        logger.debug(f"Sleeping for {self.collection_interval} seconds")
                        time.sleep(self.collection_interval)
                
                except KeyboardInterrupt:
                    logger.info("Keyboard interrupt received")
                    break
                
                except Exception as e:
                    logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
                    logger.info("Continuing after error...")
                    time.sleep(self.collection_interval)
        
        finally:
            self.stop()
    
    def stop(self) -> None:
        """Stop the application gracefully."""
        if self.running:
            logger.info("Stopping InfraGuard...")
            self.running = False
            
            # Stop health server
            if self.health_server:
                self.health_server.stop()
            
            logger.info("InfraGuard stopped")
    
    def get_status(self) -> dict:
        """
        Get application status.
        
        Returns:
            Dictionary containing status information
        """
        status = {
            'running': self.running,
            'last_collection_time': self.last_collection_time.isoformat() if self.last_collection_time else None,
            'collection_interval': self.collection_interval,
            'model_loaded': hasattr(self.detector.model, 'estimators_'),
            'slack_enabled': self.alert_manager.slack_enabled,
            'jira_enabled': self.alert_manager.jira_enabled,
            'forecasting_enabled': self.forecasting_enabled
        }
        
        if self.forecasting_enabled:
            status['last_forecast_time'] = self.last_forecast_time.isoformat() if self.last_forecast_time else None
            status['forecast_interval'] = self.forecast_interval
        
        return status
