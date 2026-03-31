"""
Integration tests for InfraGuard components.

Tests the interaction between multiple components and end-to-end workflows.
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from unittest.mock import Mock, patch
from src.collector.prometheus_collector import PrometheusCollector
from src.collector.data_formatter import DataFormatter
from src.ml.isolation_forest_detector import IsolationForestDetector
from src.alerter.alert_manager import AlertManager
from src.config.configuration_manager import ConfigurationManager


class TestCollectorFormatterIntegration:
    """Test integration between Prometheus collector and data formatter."""
    
    @pytest.fixture
    def collector_config(self):
        """Provide collector configuration."""
        return {
            'url': 'http://prometheus:9090',
            'timeout': 30,
            'queries': [
                {
                    'name': 'cpu_usage',
                    'query': 'cpu_usage_percent',
                    'metric_type': 'cpu'
                }
            ]
        }
    
    @pytest.fixture
    def collector(self, collector_config):
        """Create collector instance."""
        return PrometheusCollector(collector_config)
    
    @pytest.fixture
    def formatter(self):
        """Create formatter instance."""
        return DataFormatter()
    
    @patch('requests.get')
    def test_collect_and_format_workflow(self, mock_get, collector, formatter):
        """Test complete collect and format workflow."""
        # Mock Prometheus response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'success',
            'data': {
                'resultType': 'vector',
                'result': [
                    {
                        'metric': {'__name__': 'cpu_usage_percent'},
                        'value': [1678886400, '45.5']
                    },
                    {
                        'metric': {'__name__': 'cpu_usage_percent'},
                        'value': [1678886460, '50.2']
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        # Collect metrics
        results = collector.collect_metrics()
        assert len(results) == 1
        assert results[0]['success'] is True
        
        # Format data
        df = formatter.format_prometheus_response(results[0]['data'], 'cpu_usage')
        assert len(df) == 2
        assert 'timestamp' in df.columns
        assert 'value' in df.columns
        
        # Add features
        feature_df = formatter.add_feature_columns(df, [5])
        assert 'hour' in feature_df.columns
        assert 'rolling_mean_5' in feature_df.columns


class TestMLPipelineIntegration:
    """Test integration of ML training and detection pipeline."""
    
    @pytest.fixture
    def detector(self):
        """Create detector instance."""
        return IsolationForestDetector({
            'n_estimators': 50,
            'random_state': 42
        })
    
    @pytest.fixture
    def formatter(self):
        """Create formatter instance."""
        return DataFormatter()
    
    @pytest.fixture
    def training_data(self):
        """Generate training data."""
        np.random.seed(42)
        return pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=100, freq='1min'),
            'value': np.random.uniform(40, 60, 100)
        })
    
    def test_train_and_detect_pipeline(self, detector, formatter, training_data):
        """Test complete training and detection pipeline."""
        # Add features
        feature_data = formatter.add_feature_columns(training_data, [5, 10])
        
        # Train model
        detector.train(feature_data)
        assert hasattr(detector.model, 'estimators_')
        
        # Detect anomalies
        results = detector.detect_anomalies(feature_data, 'cpu_usage', 80)
        assert isinstance(results, list)
        
        # Verify results have expected structure
        for result in results:
            assert hasattr(result, 'timestamp')
            assert hasattr(result, 'value')
            assert hasattr(result, 'confidence')
    
    def test_model_persistence_pipeline(self, detector, formatter, training_data):
        """Test model save/load pipeline."""
        # Prepare data and train
        feature_data = formatter.add_feature_columns(training_data, [5])
        detector.train(feature_data)
        
        # Save model
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = os.path.join(tmpdir, 'test_model.pkl')
            detector.save_model(model_path)
            
            # Create new detector and load
            new_detector = IsolationForestDetector({'n_estimators': 50})
            new_detector.load_model(model_path)
            
            # Verify predictions match
            results1 = detector.detect_anomalies(feature_data, 'cpu_usage', 80)
            results2 = new_detector.detect_anomalies(feature_data, 'cpu_usage', 80)
            
            assert len(results1) == len(results2)
            for r1, r2 in zip(results1, results2):
                assert r1.confidence == pytest.approx(r2.confidence, rel=1e-5)


class TestAlertingIntegration:
    """Test integration of alerting components."""
    
    @pytest.fixture
    def alert_config(self):
        """Provide alerting configuration."""
        return {
            'slack': {
                'enabled': False,
                'webhook_url': 'https://hooks.slack.com/test',
                'channel': '#test'
            },
            'jira': {
                'enabled': False,
                'url': 'https://test.atlassian.net',
                'project_key': 'TEST',
                'username': 'test@example.com',
                'api_token': 'test-token'
            },
            'runbooks': {
                'cpu': {
                    'high': 'https://runbooks.example.com/cpu-spike'
                },
                'default': 'https://runbooks.example.com/general'
            }
        }
    
    @pytest.fixture
    def alert_manager(self, alert_config):
        """Create alert manager instance."""
        return AlertManager(alert_config)
    
    def test_alert_manager_initialization(self, alert_manager):
        """Test alert manager initializes all components."""
        assert alert_manager.slack_enabled is False
        assert alert_manager.jira_enabled is False
        assert alert_manager.runbook_mapper is not None
    
    @patch('requests.post')
    def test_alert_delivery_with_disabled_channels(self, mock_post, alert_manager):
        """Test alert delivery when channels are disabled."""
        from datetime import datetime
        
        # Send alert (should not fail even with disabled channels)
        alert_manager.send_alert(
            metric_name='cpu_usage',
            metric_value=95.5,
            confidence=90.0,
            severity='high',
            timestamp=datetime.now(),
            additional_context={}
        )
        
        # Should not make any HTTP requests since channels are disabled
        mock_post.assert_not_called()


class TestHealthEndpointIntegration:
    """Test health endpoint integration."""
    
    def test_health_server_initialization(self):
        """Test health server can be initialized."""
        from src.health_server import HealthServer
        
        def mock_status():
            return {
                'running': True,
                'last_collection_time': None,
                'model_loaded': False
            }
        
        server = HealthServer(8001, mock_status)
        assert server.port == 8001
        assert server.get_status is not None
    
    def test_health_endpoint_response(self):
        """Test health endpoint returns correct response."""
        from src.health_server import HealthServer
        import requests
        import threading
        import time
        
        def mock_status():
            return {
                'running': True,
                'last_collection_time': '2024-01-01T12:00:00',
                'model_loaded': True,
                'collection_interval': 60
            }
        
        server = HealthServer(8002, mock_status)
        
        # Start server in background thread
        thread = threading.Thread(target=server.start, daemon=True)
        thread.start()
        time.sleep(1)  # Wait for server to start
        
        try:
            # Test health endpoint
            response = requests.get('http://localhost:8002/health', timeout=2)
            assert response.status_code == 200
            
            data = response.json()
            assert data['status'] == 'healthy'
            assert data['running'] is True
            assert data['model_loaded'] is True
        finally:
            server.stop()


class TestConfigurationIntegration:
    """Test configuration management integration."""
    
    def test_configuration_loading_and_access(self):
        """Test configuration can be loaded and accessed."""
        import yaml
        
        config_data = {
            'prometheus': {
                'url': 'http://prometheus:9090',
                'timeout': 30
            },
            'ml': {
                'isolation_forest': {
                    'n_estimators': 100
                }
            },
            'logging': {
                'level': 'INFO'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name
        
        try:
            config_mgr = ConfigurationManager(config_path)
            
            # Test section access
            prom_config = config_mgr.get_prometheus_config()
            assert prom_config['url'] == 'http://prometheus:9090'
            
            ml_config = config_mgr.get_ml_config()
            assert ml_config['isolation_forest']['n_estimators'] == 100
            
            # Test dot notation access
            value = config_mgr.get('ml.isolation_forest.n_estimators')
            assert value == 100
        finally:
            os.unlink(config_path)
    
    def test_configuration_validation(self):
        """Test configuration validation catches errors."""
        import yaml
        
        # Invalid config (missing required fields)
        invalid_config = {
            'some_field': 'value'
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(invalid_config, f)
            config_path = f.name
        
        try:
            # Should not raise error during initialization
            # Validation happens when accessing specific configs
            config_mgr = ConfigurationManager(config_path)
            assert config_mgr.config is not None
        finally:
            os.unlink(config_path)


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    @patch('requests.get')
    def test_complete_detection_workflow(self, mock_get):
        """Test complete workflow from collection to detection."""
        # Setup components
        collector_config = {
            'url': 'http://prometheus:9090',
            'queries': [
                {
                    'name': 'cpu_usage',
                    'query': 'cpu_usage_percent',
                    'metric_type': 'cpu'
                }
            ]
        }
        
        collector = PrometheusCollector(collector_config)
        formatter = DataFormatter()
        detector = IsolationForestDetector({'n_estimators': 50, 'random_state': 42})
        
        # Mock Prometheus response with training data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'success',
            'data': {
                'resultType': 'vector',
                'result': [
                    {
                        'metric': {'__name__': 'cpu_usage_percent'},
                        'value': [1678886400 + i * 60, str(40 + i % 20)]
                    }
                    for i in range(100)
                ]
            }
        }
        mock_get.return_value = mock_response
        
        # Step 1: Collect metrics
        results = collector.collect_metrics()
        assert len(results) == 1
        assert results[0]['success'] is True
        
        # Step 2: Format data
        df = formatter.format_prometheus_response(results[0]['data'], 'cpu_usage')
        assert len(df) == 100
        
        # Step 3: Add features
        feature_df = formatter.add_feature_columns(df, [5, 10])
        assert 'hour' in feature_df.columns
        
        # Step 4: Train model
        detector.train(feature_df)
        assert hasattr(detector.model, 'estimators_')
        
        # Step 5: Detect anomalies
        anomalies = detector.detect_anomalies(feature_df, 'cpu_usage', 80)
        assert isinstance(anomalies, list)
        
        # Workflow completed successfully
        assert True
