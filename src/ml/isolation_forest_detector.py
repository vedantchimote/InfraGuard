"""
Isolation Forest anomaly detector for InfraGuard.

This module implements anomaly detection using scikit-learn's Isolation Forest
algorithm with model persistence and confidence scoring.
"""

import logging
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from sklearn.ensemble import IsolationForest


logger = logging.getLogger(__name__)


@dataclass
class AnomalyResult:
    """
    Encapsulates anomaly detection results.
    
    Attributes:
        is_anomaly: Boolean indicating if data point is anomalous
        anomaly_score: Raw anomaly score from model (-1 to 1)
        confidence: Confidence percentage (0 to 100)
        metric_name: Name of the metric
        timestamp: Timestamp of the data point
        value: Original metric value
        features: Dictionary of feature values used for detection
    """
    is_anomaly: bool
    anomaly_score: float
    confidence: float
    metric_name: str
    timestamp: Any
    value: float
    features: Dict[str, float]


class IsolationForestDetectorError(Exception):
    """Base exception for detector errors."""
    pass


class IsolationForestDetector:
    """
    Anomaly detector using Isolation Forest algorithm.
    
    This class provides anomaly detection capabilities using scikit-learn's
    Isolation Forest, with support for model training, persistence, and
    confidence-based scoring.
    
    Attributes:
        model: Trained IsolationForest model
        config: Configuration dictionary
        feature_columns: List of feature column names
    
    Example:
        >>> config = {
        ...     'n_estimators': 100,
        ...     'contamination': 0.1,
        ...     'random_state': 42
        ... }
        >>> detector = IsolationForestDetector(config)
        >>> detector.train(training_data)
        >>> results = detector.detect_anomalies(new_data, 'cpu_usage', 80)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Isolation Forest detector.
        
        Args:
            config: Configuration dictionary containing:
                - n_estimators: Number of trees in the forest
                - max_samples: Number of samples to draw for each tree
                - contamination: Expected proportion of anomalies
                - random_state: Random seed for reproducibility
                - max_features: Number of features to draw for each tree
        """
        self.config = config
        self.model = IsolationForest(
            n_estimators=config.get('n_estimators', 100),
            max_samples=config.get('max_samples', 'auto'),
            contamination=config.get('contamination', 0.1),
            random_state=config.get('random_state', 42),
            max_features=config.get('max_features', 1.0)
        )
        self.feature_columns: Optional[List[str]] = None
        
        logger.info(f"Initialized IsolationForestDetector with {config.get('n_estimators', 100)} estimators")
    
    def _validate_input(self, df: pd.DataFrame) -> None:
        """
        Validate that DataFrame has required feature columns.
        
        Args:
            df: Input DataFrame
        
        Raises:
            IsolationForestDetectorError: If required columns are missing
        """
        if df.empty:
            raise IsolationForestDetectorError("Input DataFrame is empty")
        
        if 'value' not in df.columns:
            raise IsolationForestDetectorError("DataFrame must have 'value' column")
        
        # Check for feature columns (rolling statistics)
        feature_cols = [col for col in df.columns if col.startswith('rolling_') or col in ['hour', 'day_of_week', 'is_weekend']]
        
        if not feature_cols:
            raise IsolationForestDetectorError("DataFrame must have feature columns (rolling statistics or time features)")
        
        # If model is trained, verify feature columns match
        if self.feature_columns is not None:
            missing_cols = set(self.feature_columns) - set(df.columns)
            if missing_cols:
                raise IsolationForestDetectorError(f"Missing required feature columns: {missing_cols}")
    
    def _extract_features(self, df: pd.DataFrame) -> np.ndarray:
        """
        Extract feature columns from DataFrame and convert to numpy array.
        
        Args:
            df: Input DataFrame with feature columns
        
        Returns:
            Numpy array of shape (n_samples, n_features)
        """
        if self.feature_columns is None:
            # First time: determine feature columns
            self.feature_columns = [
                col for col in df.columns 
                if col.startswith('rolling_') or col in ['hour', 'day_of_week', 'is_weekend', 'value']
            ]
            logger.info(f"Using {len(self.feature_columns)} features: {self.feature_columns}")
        
        # Extract features
        features = df[self.feature_columns].values
        
        # Handle NaN values
        if np.isnan(features).any():
            logger.warning("NaN values detected in features, filling with column means")
            features = pd.DataFrame(features, columns=self.feature_columns).fillna(method='ffill').fillna(method='bfill').fillna(0).values
        
        return features
    
    def train(self, df: pd.DataFrame) -> None:
        """
        Train Isolation Forest model on historical data.
        
        Args:
            df: Training DataFrame with feature columns
        
        Raises:
            IsolationForestDetectorError: If training fails
        
        Example:
            >>> detector.train(historical_data)
        """
        try:
            self._validate_input(df)
            
            logger.info(f"Training Isolation Forest on {len(df)} samples")
            
            # Extract features
            X = self._extract_features(df)
            
            # Train model
            self.model.fit(X)
            
            logger.info("Model training completed successfully")
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise IsolationForestDetectorError(f"Failed to train model: {e}") from e
    
    def save_model(self, model_path: str) -> None:
        """
        Serialize and save trained model to disk.
        
        Args:
            model_path: Path where model should be saved
        
        Raises:
            IsolationForestDetectorError: If model hasn't been trained or save fails
        
        Example:
            >>> detector.save_model('models/pretrained/isolation_forest.pkl')
        """
        if not hasattr(self.model, 'estimators_'):
            raise IsolationForestDetectorError("Model must be trained before saving")
        
        try:
            # Ensure directory exists
            Path(model_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save model and feature columns
            model_data = {
                'model': self.model,
                'feature_columns': self.feature_columns,
                'config': self.config
            }
            
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model saved to {model_path}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise IsolationForestDetectorError(f"Failed to save model: {e}") from e
    
    def load_model(self, model_path: str) -> None:
        """
        Load trained model from disk.
        
        Args:
            model_path: Path to saved model file
        
        Raises:
            IsolationForestDetectorError: If model file doesn't exist or load fails
        
        Example:
            >>> detector.load_model('models/pretrained/isolation_forest.pkl')
        """
        if not Path(model_path).exists():
            raise IsolationForestDetectorError(f"Model file not found: {model_path}")
        
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.feature_columns = model_data['feature_columns']
            self.config = model_data.get('config', self.config)
            
            logger.info(f"Model loaded from {model_path}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise IsolationForestDetectorError(f"Failed to load model: {e}") from e
    
    def compute_confidence(self, anomaly_score: float) -> float:
        """
        Convert anomaly score to confidence percentage.
        
        Isolation Forest scores range from approximately -0.5 to 0.5,
        where negative values indicate anomalies. This method converts
        scores to a 0-100 confidence scale.
        
        Args:
            anomaly_score: Raw anomaly score from model
        
        Returns:
            Confidence percentage (0-100)
        """
        # Normalize score to 0-100 range
        # More negative scores = higher confidence of anomaly
        confidence = max(0, min(100, (-anomaly_score + 0.5) * 100))
        return confidence
    
    def detect_anomalies(
        self,
        df: pd.DataFrame,
        metric_name: str,
        confidence_threshold: float = 80.0
    ) -> List[AnomalyResult]:
        """
        Detect anomalies in new data using trained model.
        
        Args:
            df: DataFrame with feature columns
            metric_name: Name of the metric being analyzed
            confidence_threshold: Minimum confidence to flag as anomaly
        
        Returns:
            List of AnomalyResult objects
        
        Raises:
            IsolationForestDetectorError: If model hasn't been trained or detection fails
        
        Example:
            >>> results = detector.detect_anomalies(new_data, 'cpu_usage', 80)
            >>> for result in results:
            ...     if result.is_anomaly:
            ...         print(f"Anomaly detected: {result.confidence}% confidence")
        """
        if not hasattr(self.model, 'estimators_'):
            raise IsolationForestDetectorError("Model must be trained or loaded before detection")
        
        try:
            self._validate_input(df)
            
            # Extract features
            X = self._extract_features(df)
            
            # Predict anomaly scores
            scores = self.model.score_samples(X)
            predictions = self.model.predict(X)
            
            # Create results
            results = []
            for idx, (score, pred) in enumerate(zip(scores, predictions)):
                confidence = self.compute_confidence(score)
                is_anomaly = (pred == -1) and (confidence >= confidence_threshold)
                
                # Extract feature values for this sample
                features = {col: df.iloc[idx][col] for col in self.feature_columns if col in df.columns}
                
                result = AnomalyResult(
                    is_anomaly=is_anomaly,
                    anomaly_score=float(score),
                    confidence=confidence,
                    metric_name=metric_name,
                    timestamp=df.iloc[idx].get('timestamp', idx),
                    value=float(df.iloc[idx]['value']),
                    features=features
                )
                results.append(result)
            
            anomaly_count = sum(1 for r in results if r.is_anomaly)
            logger.info(f"Detected {anomaly_count} anomalies out of {len(results)} samples for {metric_name}")
            
            return results
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            raise IsolationForestDetectorError(f"Failed to detect anomalies: {e}") from e
