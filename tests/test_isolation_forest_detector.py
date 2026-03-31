"""
Unit tests for IsolationForestDetector.

Tests anomaly detection, model training, and persistence.
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from pathlib import Path
from src.ml.isolation_forest_detector import IsolationForestDetector, AnomalyResult


class TestIsolationForestDetector:
    """Test suite for IsolationForestDetector class."""
    
    @pytest.fixture
    def config(self):
        """Provide test configuration."""
        return {
            'n_estimators': 100,
            'max_samples': 256,
            'contamination': 0.1,
            'random_state': 42
        }
    
    @pytest.fixture
    def detector(self, config):
        """Create IsolationForestDetector instance."""
        return IsolationForestDetector(config)
    
    @pytest.fixture
    def sample_data(self):
        """Provide sample training data."""
        np.random.seed(42)
        return pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=100, freq='1min'),
            'value': np.random.uniform(40, 60, 100),
            'hour': np.random.randint(0, 24, 100),
            'day_of_week': np.random.randint(0, 7, 100),
            'is_weekend': np.random.randint(0, 2, 100)
        })
    
    def test_initialization(self, detector, config):
        """Test detector initializes with correct configuration."""
        assert detector.n_estimators == 100
        assert detector.max_samples == 256
        assert detector.contamination == 0.1
        assert detector.random_state == 42
    
    def test_train_model(self, detector, sample_data):
        """Test model training."""
        detector.train(sample_data)
        
        # Check model is trained
        assert hasattr(detector.model, 'estimators_')
        assert len(detector.model.estimators_) == 100
    
    def test_train_with_insufficient_data(self, detector):
        """Test training with insufficient data."""
        small_data = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=5, freq='1min'),
            'value': [50.0] * 5,
            'hour': [12] * 5,
            'day_of_week': [1] * 5,
            'is_weekend': [0] * 5
        })
        
        with pytest.raises(ValueError, match="Insufficient data"):
            detector.train(small_data)
    
    def test_detect_anomalies_without_training(self, detector, sample_data):
        """Test anomaly detection without training."""
        with pytest.raises(ValueError, match="Model not trained"):
            detector.detect_anomalies(sample_data, 'cpu_usage', 80)
    
    def test_detect_anomalies_after_training(self, detector, sample_data):
        """Test anomaly detection after training."""
        # Train model
        detector.train(sample_data)
        
        # Detect anomalies
        results = detector.detect_anomalies(sample_data, 'cpu_usage', 80)
        
        assert isinstance(results, list)
        assert all(isinstance(r, AnomalyResult) for r in results)
        
        # Check result attributes
        if len(results) > 0:
            result = results[0]
            assert hasattr(result, 'timestamp')
            assert hasattr(result, 'value')
            assert hasattr(result, 'anomaly_score')
            assert hasattr(result, 'confidence')
            assert hasattr(result, 'is_anomaly')
    
    def test_anomaly_result_dataclass(self):
        """Test AnomalyResult dataclass."""
        from datetime import datetime
        
        result = AnomalyResult(
            timestamp=datetime(2024, 1, 1, 12, 0),
            value=95.5,
            anomaly_score=-0.15,
            confidence=85.0,
            is_anomaly=True
        )
        
        assert result.timestamp == datetime(2024, 1, 1, 12, 0)
        assert result.value == 95.5
        assert result.anomaly_score == -0.15
        assert result.confidence == 85.0
        assert result.is_anomaly is True
    
    def test_save_and_load_model(self, detector, sample_data):
        """Test model serialization and deserialization."""
        # Train model
        detector.train(sample_data)
        
        # Save model
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = os.path.join(tmpdir, 'test_model.pkl')
            detector.save_model(model_path)
            
            # Check file exists
            assert os.path.exists(model_path)
            
            # Create new detector and load model
            new_detector = IsolationForestDetector({'n_estimators': 100})
            new_detector.load_model(model_path)
            
            # Check model is loaded
            assert hasattr(new_detector.model, 'estimators_')
            
            # Test predictions are consistent
            results1 = detector.detect_anomalies(sample_data, 'cpu_usage', 80)
            results2 = new_detector.detect_anomalies(sample_data, 'cpu_usage', 80)
            
            assert len(results1) == len(results2)
    
    def test_load_nonexistent_model(self, detector):
        """Test loading non-existent model file."""
        with pytest.raises(FileNotFoundError):
            detector.load_model('/nonexistent/path/model.pkl')
    
    def test_confidence_calculation(self, detector, sample_data):
        """Test confidence percentage calculation."""
        detector.train(sample_data)
        results = detector.detect_anomalies(sample_data, 'cpu_usage', 80)
        
        # Check confidence is between 0 and 100
        for result in results:
            assert 0 <= result.confidence <= 100
    
    def test_threshold_filtering(self, detector, sample_data):
        """Test that only anomalies above threshold are returned."""
        detector.train(sample_data)
        
        # High threshold should return fewer anomalies
        results_high = detector.detect_anomalies(sample_data, 'cpu_usage', 95)
        results_low = detector.detect_anomalies(sample_data, 'cpu_usage', 50)
        
        assert len(results_high) <= len(results_low)
    
    def test_feature_extraction(self, detector, sample_data):
        """Test feature extraction from DataFrame."""
        features = detector._extract_features(sample_data)
        
        assert isinstance(features, np.ndarray)
        assert features.shape[0] == len(sample_data)
        # Should have value + time features
        assert features.shape[1] >= 4  # value, hour, day_of_week, is_weekend
    
    def test_input_validation(self, detector, sample_data):
        """Test input validation."""
        detector.train(sample_data)
        
        # Missing required columns
        invalid_data = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=10, freq='1min'),
            'value': [50.0] * 10
            # Missing hour, day_of_week, is_weekend
        })
        
        with pytest.raises(ValueError, match="Missing required feature columns"):
            detector.detect_anomalies(invalid_data, 'cpu_usage', 80)
