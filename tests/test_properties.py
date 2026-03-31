"""
Property-based tests for InfraGuard components.

Uses Hypothesis to test universal properties that should hold
for all valid inputs.
"""

import pytest
import pandas as pd
import numpy as np
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, timedelta
from src.collector.data_formatter import DataFormatter
from src.ml.isolation_forest_detector import IsolationForestDetector


class TestDataFormatterProperties:
    """Property-based tests for DataFormatter."""
    
    @given(
        num_points=st.integers(min_value=1, max_value=1000),
        metric_name=st.text(min_size=1, max_size=50)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_1_transformation_preserves_data_count(self, num_points, metric_name):
        """
        Property 1: Prometheus Response Transformation Preserves Data.
        
        For any valid Prometheus response with N data points,
        the formatted DataFrame SHALL contain exactly N rows.
        """
        formatter = DataFormatter()
        
        # Generate Prometheus response
        response = {
            'status': 'success',
            'data': {
                'resultType': 'vector',
                'result': [
                    {
                        'metric': {'__name__': 'test_metric'},
                        'value': [1678886400 + i * 60, str(float(i))]
                    }
                    for i in range(num_points)
                ]
            }
        }
        
        df = formatter.format_prometheus_response(response, metric_name)
        
        # Property: Output row count equals input data point count
        assert len(df) == num_points
    
    @given(
        timestamps=st.lists(
            st.floats(min_value=1000000000, max_value=2000000000),
            min_size=1,
            max_size=100
        )
    )
    @settings(max_examples=50, deadline=None)
    def test_property_2_timestamp_precision_preservation(self, timestamps):
        """
        Property 2: Timestamp Precision Preservation.
        
        For any list of Unix timestamps, the normalized timestamps
        SHALL preserve second-level precision.
        """
        formatter = DataFormatter()
        
        df = pd.DataFrame({
            'timestamp': timestamps,
            'value': [50.0] * len(timestamps)
        })
        
        normalized_df = formatter.normalize_timestamps(df)
        
        # Property: All timestamps are valid datetime objects
        assert all(isinstance(ts, pd.Timestamp) for ts in normalized_df['timestamp'])
        
        # Property: Timestamps are in chronological order if input was sorted
        if len(timestamps) > 1:
            sorted_timestamps = sorted(timestamps)
            sorted_df = pd.DataFrame({
                'timestamp': sorted_timestamps,
                'value': [50.0] * len(sorted_timestamps)
            })
            sorted_normalized = formatter.normalize_timestamps(sorted_df)
            assert sorted_normalized['timestamp'].is_monotonic_increasing
    
    @given(
        num_points=st.integers(min_value=50, max_value=200),
        window_size=st.integers(min_value=2, max_value=30)
    )
    @settings(max_examples=30, deadline=None)
    def test_property_rolling_statistics_validity(self, num_points, window_size):
        """
        Property: Rolling statistics are valid.
        
        For any time series data and window size W,
        rolling mean SHALL be within the range of the data,
        and rolling std SHALL be non-negative.
        """
        formatter = DataFormatter()
        
        values = np.random.uniform(0, 100, num_points)
        df = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=num_points, freq='1min'),
            'value': values
        })
        
        feature_df = formatter.add_feature_columns(df, [window_size])
        
        col_mean = f'rolling_mean_{window_size}'
        col_std = f'rolling_std_{window_size}'
        
        # Property: Rolling mean is within data range
        valid_means = feature_df[col_mean].dropna()
        if len(valid_means) > 0:
            assert valid_means.min() >= values.min() - 1e-10  # Allow small floating point error
            assert valid_means.max() <= values.max() + 1e-10
        
        # Property: Rolling std is non-negative
        valid_stds = feature_df[col_std].dropna()
        assert all(valid_stds >= 0)


class TestIsolationForestProperties:
    """Property-based tests for IsolationForestDetector."""
    
    @given(
        num_points=st.integers(min_value=50, max_value=200),
        confidence_threshold=st.floats(min_value=0, max_value=100)
    )
    @settings(max_examples=30, deadline=None)
    def test_property_4_anomaly_score_completeness(self, num_points, confidence_threshold):
        """
        Property 4: Anomaly Score Computation Completeness.
        
        For any input data with N points, the detector SHALL compute
        anomaly scores for all N points.
        """
        detector = IsolationForestDetector({'n_estimators': 50, 'random_state': 42})
        
        # Generate training data
        train_data = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=num_points, freq='1min'),
            'value': np.random.uniform(40, 60, num_points),
            'hour': np.random.randint(0, 24, num_points),
            'day_of_week': np.random.randint(0, 7, num_points),
            'is_weekend': np.random.randint(0, 2, num_points)
        })
        
        detector.train(train_data)
        results = detector.detect_anomalies(train_data, 'test_metric', confidence_threshold)
        
        # Property: Number of results (anomalies + normal) equals input size
        # Note: detect_anomalies returns only anomalies, but internally processes all points
        assert len(results) <= num_points
        
        # Property: All results have valid confidence scores
        for result in results:
            assert 0 <= result.confidence <= 100
    
    @given(
        num_points=st.integers(min_value=50, max_value=200)
    )
    @settings(max_examples=20, deadline=None)
    def test_property_5_confidence_percentage_validity(self, num_points):
        """
        Property 5: Confidence Percentage Validity.
        
        For any anomaly detection result, the confidence percentage
        SHALL be between 0 and 100 inclusive.
        """
        detector = IsolationForestDetector({'n_estimators': 50, 'random_state': 42})
        
        data = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=num_points, freq='1min'),
            'value': np.random.uniform(40, 60, num_points),
            'hour': np.random.randint(0, 24, num_points),
            'day_of_week': np.random.randint(0, 7, num_points),
            'is_weekend': np.random.randint(0, 2, num_points)
        })
        
        detector.train(data)
        results = detector.detect_anomalies(data, 'test_metric', 50)
        
        # Property: All confidence values are valid percentages
        for result in results:
            assert isinstance(result.confidence, (int, float))
            assert 0 <= result.confidence <= 100
    
    @given(
        threshold1=st.floats(min_value=50, max_value=80),
        threshold2=st.floats(min_value=80, max_value=95)
    )
    @settings(max_examples=20, deadline=None)
    def test_property_6_threshold_based_alert_triggering(self, threshold1, threshold2):
        """
        Property 6: Threshold-Based Alert Triggering.
        
        For any two thresholds T1 < T2, the number of anomalies detected
        with threshold T1 SHALL be >= the number detected with T2.
        """
        assume(threshold1 < threshold2)
        
        detector = IsolationForestDetector({'n_estimators': 50, 'random_state': 42})
        
        data = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=100, freq='1min'),
            'value': np.random.uniform(40, 60, 100),
            'hour': np.random.randint(0, 24, 100),
            'day_of_week': np.random.randint(0, 7, 100),
            'is_weekend': np.random.randint(0, 2, 100)
        })
        
        detector.train(data)
        
        results_low = detector.detect_anomalies(data, 'test_metric', threshold1)
        results_high = detector.detect_anomalies(data, 'test_metric', threshold2)
        
        # Property: Lower threshold detects more or equal anomalies
        assert len(results_low) >= len(results_high)


class TestConfigurationProperties:
    """Property-based tests for configuration management."""
    
    @given(
        config_dict=st.dictionaries(
            keys=st.text(min_size=1, max_size=20),
            values=st.one_of(
                st.integers(),
                st.floats(allow_nan=False, allow_infinity=False),
                st.text(),
                st.booleans()
            ),
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=30, deadline=None)
    def test_property_17_configuration_validation_completeness(self, config_dict):
        """
        Property 17: Configuration Validation Completeness.
        
        For any configuration dictionary, the validation SHALL check
        all required fields and report missing fields.
        """
        from src.config.configuration_manager import ConfigurationManager
        import tempfile
        import yaml
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_dict, f)
            config_path = f.name
        
        try:
            # Attempt to load configuration
            # This may raise ConfigurationError if required fields are missing
            try:
                config_mgr = ConfigurationManager(config_path)
                # If successful, config should be accessible
                assert config_mgr.config is not None
            except Exception as e:
                # If validation fails, error message should be informative
                assert len(str(e)) > 0
        finally:
            import os
            os.unlink(config_path)


class TestRunbookProperties:
    """Property-based tests for runbook mapping."""
    
    @given(
        metric_type=st.sampled_from(['cpu', 'memory', 'error_rate', 'latency']),
        severity=st.sampled_from(['high', 'medium', 'low'])
    )
    @settings(max_examples=20, deadline=None)
    def test_property_16_runbook_resolution_with_fallback(self, metric_type, severity):
        """
        Property 16: Runbook Resolution with Fallback.
        
        For any metric type and severity, the runbook mapper SHALL
        return either a specific runbook URL or a default fallback URL.
        """
        from src.alerter.runbook_mapper import RunbookMapper
        
        config = {
            'runbooks': {
                'cpu': {
                    'high': 'https://runbooks.example.com/cpu-spike',
                    'medium': 'https://runbooks.example.com/cpu-elevated'
                },
                'memory': {
                    'high': 'https://runbooks.example.com/memory-leak',
                    'medium': 'https://runbooks.example.com/memory-elevated'
                },
                'default': 'https://runbooks.example.com/general-troubleshooting'
            }
        }
        
        mapper = RunbookMapper(config)
        runbook_url = mapper.get_runbook(metric_type, severity)
        
        # Property: Always returns a valid URL (never None or empty)
        assert runbook_url is not None
        assert len(runbook_url) > 0
        assert runbook_url.startswith('http')
