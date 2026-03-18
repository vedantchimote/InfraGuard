"""
Time-Series Forecaster Module

This module provides time-series forecasting capabilities using Facebook Prophet
to predict future metric values and enable proactive alerting.
"""

from prophet import Prophet
import pandas as pd
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ForecastResult:
    """
    Result of time-series forecasting.
    
    Attributes:
        predictions: DataFrame with columns [ds, yhat, yhat_lower, yhat_upper]
        breach_time: Timestamp when threshold breach is predicted (None if no breach)
        breach_value: Predicted value at breach time
        confidence_interval_lower: Lower bound of prediction confidence interval
        confidence_interval_upper: Upper bound of prediction confidence interval
    """
    predictions: pd.DataFrame
    breach_time: Optional[datetime]
    breach_value: Optional[float]
    confidence_interval_lower: Optional[float]
    confidence_interval_upper: Optional[float]
    
    def to_dict(self) -> dict:
        """Convert result to dictionary for serialization."""
        return {
            "breach_predicted": self.breach_time is not None,
            "breach_time": self.breach_time.isoformat() if self.breach_time else None,
            "breach_value": self.breach_value,
            "confidence_lower": self.confidence_interval_lower,
            "confidence_upper": self.confidence_interval_upper
        }


class TimeSeriesForecaster:
    """
    Forecasts future metric values using Facebook Prophet.
    
    Prophet is designed for business time-series with:
    - Strong seasonal patterns (daily, weekly)
    - Multiple seasons of historical data
    - Missing data and outliers
    - Trend changes
    
    Attributes:
        model: Prophet model instance
        prediction_window_minutes: How far ahead to forecast (default: 15)
        thresholds: Dict mapping metric names to critical threshold values
    """
    
    def __init__(self, config: dict) -> None:
        """
        Initialize forecaster with configuration.
        
        Args:
            config: Dictionary containing:
                - prediction_window: int (seconds, default: 3600)
                - thresholds: dict[str, float] (metric name -> threshold value)
                - prophet: dict with Prophet parameters
                    - seasonality_mode: str ('additive' or 'multiplicative')
                    - changepoint_prior_scale: float (flexibility of trend)
                    - interval_width: float (confidence interval width)
        """
        # Get prediction window in minutes (convert from seconds if needed)
        prediction_window_seconds = config.get('prediction_window', 3600)
        self.prediction_window_minutes = prediction_window_seconds // 60
        
        # Get thresholds configuration
        self.thresholds = config.get('thresholds', {})
        
        # Get Prophet-specific configuration
        prophet_config = config.get('prophet', {})
        seasonality_mode = prophet_config.get('seasonality_mode', 'multiplicative')
        changepoint_prior_scale = prophet_config.get('changepoint_prior_scale', 0.05)
        interval_width = prophet_config.get('interval_width', 0.95)
        
        # Initialize Prophet with parameters
        # Suppress Prophet's verbose logging
        logging.getLogger('prophet').setLevel(logging.WARNING)
        logging.getLogger('cmdstanpy').setLevel(logging.WARNING)
        
        self.model = Prophet(
            seasonality_mode=seasonality_mode,
            changepoint_prior_scale=changepoint_prior_scale,
            interval_width=interval_width,
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=False  # Not enough data typically
        )
        
        logger.info(
            f"TimeSeriesForecaster initialized with prediction_window={self.prediction_window_minutes}min, "
            f"seasonality_mode={seasonality_mode}"
        )
    
    def forecast(self, data: pd.DataFrame, metric_name: str) -> ForecastResult:
        """
        Generate forecast for the next prediction window.
        
        Args:
            data: Historical metrics DataFrame with columns [timestamp, value]
            metric_name: Name of metric being forecasted (for threshold lookup)
        
        Returns:
            ForecastResult containing predictions and breach analysis
        
        Raises:
            ValueError: If data is insufficient for forecasting (< 2 days)
        """
        # Validate sufficient historical data (at least 2 days)
        if len(data) < 2880:  # 2 days at 1-minute intervals
            raise ValueError(
                f"Insufficient historical data for forecasting: {len(data)} points "
                f"(need >= 2880 for 2 days at 1-minute intervals)"
            )
        
        logger.info(f"Generating forecast for {metric_name} with {len(data)} historical points")
        
        # Prepare data in Prophet format
        prophet_data = self._prepare_prophet_data(data)
        
        # Fit model
        self._fit_model(prophet_data)
        
        # Create future dataframe for prediction window
        future = self.model.make_future_dataframe(
            periods=self.prediction_window_minutes,
            freq='min'  # Minute frequency (use 'min' instead of deprecated 'T')
        )
        
        # Generate forecast
        forecast = self.model.predict(future)
        
        # Extract only future predictions
        future_forecast = forecast.tail(self.prediction_window_minutes)
        
        # Check for threshold breach
        threshold = self._get_threshold(metric_name)
        breach_time = None
        breach_value = None
        confidence_lower = None
        confidence_upper = None
        
        if threshold is not None:
            breach_mask = future_forecast['yhat'] > threshold
            if breach_mask.any():
                # Find first breach
                breach_indices = breach_mask[breach_mask].index
                breach_idx = breach_indices[0]
                breach_time = future_forecast.loc[breach_idx, 'ds']
                breach_value = future_forecast.loc[breach_idx, 'yhat']
                confidence_lower = future_forecast.loc[breach_idx, 'yhat_lower']
                confidence_upper = future_forecast.loc[breach_idx, 'yhat_upper']
                
                logger.warning(
                    f"Threshold breach predicted for {metric_name} at {breach_time}: "
                    f"value={breach_value:.2f}, threshold={threshold}"
                )
        
        logger.info(
            f"Forecast generated for {metric_name}: {len(future_forecast)} predictions, "
            f"breach_predicted={breach_time is not None}"
        )
        
        return ForecastResult(
            predictions=future_forecast,
            breach_time=breach_time,
            breach_value=breach_value,
            confidence_interval_lower=confidence_lower,
            confidence_interval_upper=confidence_upper
        )
    
    def predict_threshold_breach(self, forecast: pd.DataFrame, threshold: float) -> bool:
        """
        Check if any predicted value exceeds threshold.
        
        Args:
            forecast: DataFrame from Prophet with 'yhat' column
            threshold: Critical threshold value
        
        Returns:
            True if breach is predicted, False otherwise
        """
        return (forecast['yhat'] > threshold).any()
    
    def _prepare_prophet_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Convert metrics DataFrame to Prophet format.
        
        Prophet requires columns named 'ds' (datetime) and 'y' (value).
        
        Args:
            data: DataFrame with columns [timestamp, value]
        
        Returns:
            DataFrame with columns [ds, y]
        """
        prophet_data = pd.DataFrame({
            'ds': pd.to_datetime(data['timestamp']),
            'y': data['value']
        })
        
        # Sort by timestamp
        prophet_data = prophet_data.sort_values('ds').reset_index(drop=True)
        
        return prophet_data
    
    def _fit_model(self, data: pd.DataFrame) -> None:
        """
        Fit Prophet model to historical data.
        
        Args:
            data: DataFrame in Prophet format [ds, y]
        """
        # Create a new model instance for each fit to avoid state issues
        prophet_config = {
            'seasonality_mode': self.model.seasonality_mode,
            'changepoint_prior_scale': self.model.changepoint_prior_scale,
            'interval_width': self.model.interval_width,
            'daily_seasonality': self.model.daily_seasonality,
            'weekly_seasonality': self.model.weekly_seasonality,
            'yearly_seasonality': self.model.yearly_seasonality
        }
        
        self.model = Prophet(**prophet_config)
        self.model.fit(data)
    
    def _get_threshold(self, metric_name: str) -> Optional[float]:
        """
        Get threshold value for a metric.
        
        Supports both direct metric name lookup and metric type lookup.
        For example, 'cpu_usage' might map to thresholds.cpu.severity_high
        
        Args:
            metric_name: Name of the metric
        
        Returns:
            Threshold value or None if not configured
        """
        # Try direct lookup first
        if metric_name in self.thresholds:
            threshold_value = self.thresholds[metric_name]
            # If it's a dict, extract severity_high
            if isinstance(threshold_value, dict):
                return threshold_value.get('severity_high')
            else:
                return threshold_value
        
        # Try to extract metric type (e.g., 'cpu' from 'cpu_usage')
        metric_type = metric_name.split('_')[0] if '_' in metric_name else metric_name
        
        # Look for threshold in nested structure
        if metric_type in self.thresholds:
            threshold_config = self.thresholds[metric_type]
            if isinstance(threshold_config, dict):
                # Use severity_high as the critical threshold
                return threshold_config.get('severity_high')
            else:
                return threshold_config
        
        return None
