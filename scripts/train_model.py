#!/usr/bin/env python3
"""
Model training script for InfraGuard.

This script queries historical data from Prometheus, formats it with features,
trains an Isolation Forest model, and saves it for production use.
"""

import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.configuration_manager import ConfigurationManager
from src.collector.prometheus_collector import PrometheusCollector
from src.collector.data_formatter import DataFormatter
from src.ml.isolation_forest_detector import IsolationForestDetector
from src.utils.logging_config import setup_logging


logger = logging.getLogger(__name__)


def query_historical_data(collector: PrometheusCollector, days: int = 7):
    """
    Query historical data from Prometheus.
    
    Args:
        collector: PrometheusCollector instance
        days: Number of days of historical data to query
    
    Returns:
        List of query results
    """
    logger.info(f"Querying {days} days of historical data from Prometheus")
    
    # For training, we use the current instant query
    # In production, you might want to use range queries
    results = collector.collect_metrics()
    
    successful_results = [r for r in results if r['success']]
    logger.info(f"Successfully collected {len(successful_results)} metric types")
    
    return successful_results


def format_and_combine_data(results, formatter: DataFormatter):
    """
    Format Prometheus responses and combine into single DataFrame.
    
    Args:
        results: List of Prometheus query results
        formatter: DataFormatter instance
    
    Returns:
        Combined DataFrame with all metrics
    """
    import pandas as pd
    
    all_dataframes = []
    
    for result in results:
        if not result['success']:
            continue
        
        metric_name = result['query_name']
        logger.info(f"Formatting data for {metric_name}")
        
        # Format response
        df = formatter.format_prometheus_response(result['data'], metric_name)
        
        if df.empty:
            logger.warning(f"No data for {metric_name}, skipping")
            continue
        
        # Add features
        df = formatter.add_feature_columns(df)
        
        all_dataframes.append(df)
    
    if not all_dataframes:
        raise ValueError("No data available for training")
    
    # Combine all dataframes
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    logger.info(f"Combined dataset has {len(combined_df)} samples")
    
    return combined_df


def train_and_save_model(df, config, model_path: str):
    """
    Train Isolation Forest model and save to disk.
    
    Args:
        df: Training DataFrame
        config: ML configuration dictionary
        model_path: Path where model should be saved
    """
    logger.info("Initializing Isolation Forest detector")
    
    # Get Isolation Forest config
    if_config = config.get('isolation_forest', {})
    
    # Create detector
    detector = IsolationForestDetector(if_config)
    
    # Train model
    logger.info("Training model...")
    detector.train(df)
    
    # Save model
    logger.info(f"Saving model to {model_path}")
    detector.save_model(model_path)
    
    logger.info("Model training completed successfully")


def main():
    """Main training script."""
    parser = argparse.ArgumentParser(description='Train InfraGuard anomaly detection model')
    parser.add_argument(
        '--config',
        default='config/settings.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days of historical data to use for training'
    )
    parser.add_argument(
        '--output',
        help='Output path for trained model (overrides config)'
    )
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(log_level=args.log_level)
    
    logger.info("=" * 60)
    logger.info("InfraGuard Model Training Script")
    logger.info("=" * 60)
    
    try:
        # Load configuration
        logger.info(f"Loading configuration from {args.config}")
        config_mgr = ConfigurationManager(args.config)
        
        # Get configurations
        prometheus_config = config_mgr.get_prometheus_config()
        ml_config = config_mgr.get_ml_config()
        
        # Determine model output path
        model_path = args.output or ml_config.get('model_path', 'models/pretrained/isolation_forest.pkl')
        
        # Initialize components
        logger.info("Initializing Prometheus collector")
        collector = PrometheusCollector(prometheus_config)
        
        logger.info("Initializing data formatter")
        formatter = DataFormatter()
        
        # Query historical data
        results = query_historical_data(collector, args.days)
        
        if not results:
            logger.error("No data collected from Prometheus")
            sys.exit(1)
        
        # Format and combine data
        training_data = format_and_combine_data(results, formatter)
        
        logger.info(f"Training data shape: {training_data.shape}")
        logger.info(f"Features: {[col for col in training_data.columns if col.startswith('rolling_') or col in ['hour', 'day_of_week', 'is_weekend', 'value']]}")
        
        # Train and save model
        train_and_save_model(training_data, ml_config, model_path)
        
        logger.info("=" * 60)
        logger.info("Training completed successfully!")
        logger.info(f"Model saved to: {model_path}")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.info("Training interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
