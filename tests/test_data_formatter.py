"""
Unit tests for DataFormatter.

Tests data transformation, timestamp normalization, and feature engineering.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from src.collector.data_formatter import DataFormatter


class TestDataFormatter:
    """Test suite for DataFormatter class."""
    
    @pytest.fixture
    def formatter(self):
        """Create DataFormatter instance."""
        return DataFormatter()
    
    @pytest.fixture
    def sample_prometheus_response(self):
        """Provide sample Prometheus response."""
        return {
            'status': 'success',
            'data': {
                'resultType': 'vector',
                'result': [
                    {
                        'metric': {'__name__': 'cpu_usage_percent', 'instance': 'localhost:8080'},
                        'value': [1678886400, '45.5']
                    },
                    {
                        'metric': {'__name__': 'cpu_usage_percent', 'instance': 'localhost:8080'},
                        'value': [1678886460, '50.2']
                    }
                ]
            }
        }
    
    def test_format_prometheus_response_success(self, formatter, sample_prometheus_response):
        """Test successful Prometheus response formatting."""
        df = formatter.format_prometheus_response(sample_prometheus_response, 'cpu_usage')
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert 'timestamp' in df.columns
        assert 'value' in df.columns
        assert 'metric_name' in df.columns
        assert df['metric_name'].iloc[0] == 'cpu_usage'
    
    def test_format_prometheus_response_empty_result(self, formatter):
        """Test formatting empty Prometheus response."""
        empty_response = {
            'status': 'success',
            'data': {
                'resultType': 'vector',
                'result': []
            }
        }
        
        df = formatter.format_prometheus_response(empty_response, 'cpu_usage')
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
    
    def test_format_prometheus_response_invalid_status(self, formatter):
        """Test formatting response with error status."""
        error_response = {
            'status': 'error',
            'error': 'query failed'
        }
        
        df = formatter.format_prometheus_response(error_response, 'cpu_usage')
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
    
    def test_normalize_timestamps(self, formatter):
        """Test timestamp normalization."""
        df = pd.DataFrame({
            'timestamp': [1678886400.123, 1678886460.456],
            'value': [45.5, 50.2]
        })
        
        normalized_df = formatter.normalize_timestamps(df)
        
        assert 'timestamp' in normalized_df.columns
        # Check timestamps are datetime objects
        assert isinstance(normalized_df['timestamp'].iloc[0], pd.Timestamp)
    
    def test_add_feature_columns(self, formatter):
        """Test feature column addition."""
        df = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=100, freq='1min'),
            'value': np.random.uniform(40, 60, 100)
        })
        
        rolling_windows = [5, 10, 30]
        feature_df = formatter.add_feature_columns(df, rolling_windows)
        
        # Check time-based features
        assert 'hour' in feature_df.columns
        assert 'day_of_week' in feature_df.columns
        assert 'is_weekend' in feature_df.columns
        
        # Check rolling statistics
        assert 'rolling_mean_5' in feature_df.columns
        assert 'rolling_std_5' in feature_df.columns
        assert 'rolling_mean_10' in feature_df.columns
        assert 'rolling_std_10' in feature_df.columns
        
        # Check value ranges
        assert feature_df['hour'].min() >= 0
        assert feature_df['hour'].max() <= 23
        assert feature_df['day_of_week'].min() >= 0
        assert feature_df['day_of_week'].max() <= 6
        assert feature_df['is_weekend'].isin([0, 1]).all()
    
    def test_add_feature_columns_empty_dataframe(self, formatter):
        """Test feature addition with empty DataFrame."""
        df = pd.DataFrame(columns=['timestamp', 'value'])
        
        feature_df = formatter.add_feature_columns(df, [5, 10])
        
        assert isinstance(feature_df, pd.DataFrame)
        assert len(feature_df) == 0
    
    def test_value_conversion_to_float(self, formatter):
        """Test that string values are converted to float."""
        response = {
            'status': 'success',
            'data': {
                'resultType': 'vector',
                'result': [
                    {
                        'metric': {'__name__': 'cpu_usage_percent'},
                        'value': [1678886400, '45.5']  # String value
                    }
                ]
            }
        }
        
        df = formatter.format_prometheus_response(response, 'cpu_usage')
        
        assert df['value'].dtype == np.float64
        assert df['value'].iloc[0] == 45.5
    
    def test_rolling_statistics_calculation(self, formatter):
        """Test rolling statistics are calculated correctly."""
        # Create DataFrame with known values
        df = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=10, freq='1min'),
            'value': [10.0] * 10  # All values are 10
        })
        
        feature_df = formatter.add_feature_columns(df, [5])
        
        # Rolling mean of constant values should be the constant
        assert feature_df['rolling_mean_5'].dropna().iloc[0] == pytest.approx(10.0)
        # Rolling std of constant values should be 0
        assert feature_df['rolling_std_5'].dropna().iloc[0] == pytest.approx(0.0)
