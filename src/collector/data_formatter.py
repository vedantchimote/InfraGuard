"""
Data formatter for Prometheus responses.

This module transforms Prometheus API responses into structured DataFrames
with normalized timestamps and computed feature columns.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


class DataFormatterError(Exception):
    """Base exception for data formatting errors."""
    pass


class DataFormatter:
    """
    Transforms Prometheus API responses into structured DataFrames.
    
    This class handles conversion of Prometheus JSON responses to Pandas DataFrames,
    normalizes timestamps to second-level precision, and computes rolling statistics
    and time-based features for ML model input.
    
    Example:
        >>> formatter = DataFormatter()
        >>> prometheus_response = {...}  # Prometheus API response
        >>> df = formatter.format_prometheus_response(prometheus_response, 'cpu_usage')
        >>> df = formatter.add_feature_columns(df)
    """
    
    def __init__(self):
        """Initialize DataFormatter."""
        logger.info("Initialized DataFormatter")
    
    def format_prometheus_response(
        self,
        response: Dict[str, Any],
        metric_name: str
    ) -> pd.DataFrame:
        """
        Convert Prometheus API response JSON to Pandas DataFrame.
        
        Args:
            response: Prometheus API response dictionary
            metric_name: Name of the metric being formatted
        
        Returns:
            DataFrame with columns: timestamp, value, metric_name, and label columns
        
        Raises:
            DataFormatterError: If response format is invalid
        
        Example:
            >>> response = {
            ...     'data': {
            ...         'result': [
            ...             {
            ...                 'metric': {'instance': 'localhost:9090'},
            ...                 'value': [1609459200, '42.5']
            ...             }
            ...         ]
            ...     }
            ... }
            >>> df = formatter.format_prometheus_response(response, 'cpu_usage')
        """
        try:
            # Extract result array from response
            if 'data' not in response or 'result' not in response['data']:
                raise DataFormatterError("Invalid Prometheus response format: missing 'data.result'")
            
            results = response['data']['result']
            
            if not results:
                logger.warning(f"No data returned for metric: {metric_name}")
                # Return empty DataFrame with expected columns
                return pd.DataFrame(columns=['timestamp', 'value', 'metric_name'])
            
            # Parse each result into rows
            rows = []
            for result in results:
                metric_labels = result.get('metric', {})
                
                # Handle both instant vector (value) and range vector (values)
                if 'value' in result:
                    timestamp, value = result['value']
                    rows.append({
                        'timestamp': timestamp,
                        'value': float(value),
                        'metric_name': metric_name,
                        **metric_labels
                    })
                elif 'values' in result:
                    for timestamp, value in result['values']:
                        rows.append({
                            'timestamp': timestamp,
                            'value': float(value),
                            'metric_name': metric_name,
                            **metric_labels
                        })
            
            if not rows:
                logger.warning(f"No valid data points for metric: {metric_name}")
                return pd.DataFrame(columns=['timestamp', 'value', 'metric_name'])
            
            # Create DataFrame
            df = pd.DataFrame(rows)
            
            # Normalize timestamps
            df = self.normalize_timestamps(df)
            
            logger.info(f"Formatted {len(df)} data points for metric: {metric_name}")
            return df
            
        except Exception as e:
            logger.error(f"Error formatting Prometheus response: {e}")
            raise DataFormatterError(f"Failed to format response: {e}") from e
    
    def normalize_timestamps(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize timestamps to second-level precision.
        
        Converts Unix timestamps to datetime objects and ensures consistent
        second-level precision (no milliseconds).
        
        Args:
            df: DataFrame with 'timestamp' column (Unix timestamp)
        
        Returns:
            DataFrame with normalized timestamp column as datetime
        
        Example:
            >>> df = pd.DataFrame({'timestamp': [1609459200.123, 1609459201.456]})
            >>> df = formatter.normalize_timestamps(df)
            >>> df['timestamp'].dtype
            dtype('<M8[ns]')
        """
        if 'timestamp' not in df.columns:
            logger.warning("No timestamp column found, skipping normalization")
            return df
        
        try:
            # Convert to datetime, handling both seconds and milliseconds
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            
            # Round to nearest second for consistency
            df['timestamp'] = df['timestamp'].dt.floor('s')
            
            # Sort by timestamp
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            logger.debug(f"Normalized {len(df)} timestamps")
            return df
            
        except Exception as e:
            logger.error(f"Error normalizing timestamps: {e}")
            raise DataFormatterError(f"Failed to normalize timestamps: {e}") from e
    
    def add_feature_columns(
        self,
        df: pd.DataFrame,
        rolling_windows: Optional[List[int]] = None
    ) -> pd.DataFrame:
        """
        Add computed feature columns for ML model input.
        
        Computes rolling statistics (mean, std, min, max) and time-based features
        (hour, day_of_week, is_weekend) to enrich the dataset for anomaly detection.
        
        Args:
            df: DataFrame with 'timestamp' and 'value' columns
            rolling_windows: List of window sizes for rolling statistics (default: [5, 10, 30])
        
        Returns:
            DataFrame with additional feature columns
        
        Example:
            >>> df = pd.DataFrame({
            ...     'timestamp': pd.date_range('2024-01-01', periods=100, freq='1min'),
            ...     'value': np.random.randn(100)
            ... })
            >>> df = formatter.add_feature_columns(df)
            >>> 'rolling_mean_5' in df.columns
            True
        """
        if rolling_windows is None:
            rolling_windows = [5, 10, 30]
        
        if df.empty:
            logger.warning("Empty DataFrame, skipping feature computation")
            return df
        
        if 'value' not in df.columns:
            raise DataFormatterError("DataFrame must have 'value' column")
        
        try:
            df = df.copy()
            
            # Compute rolling statistics
            for window in rolling_windows:
                if len(df) >= window:
                    df[f'rolling_mean_{window}'] = df['value'].rolling(window=window, min_periods=1).mean()
                    df[f'rolling_std_{window}'] = df['value'].rolling(window=window, min_periods=1).std()
                    df[f'rolling_min_{window}'] = df['value'].rolling(window=window, min_periods=1).min()
                    df[f'rolling_max_{window}'] = df['value'].rolling(window=window, min_periods=1).max()
                else:
                    logger.warning(f"Not enough data points for window size {window}")
            
            # Add time-based features if timestamp column exists
            if 'timestamp' in df.columns and pd.api.types.is_datetime64_any_dtype(df['timestamp']):
                df['hour'] = df['timestamp'].dt.hour
                df['day_of_week'] = df['timestamp'].dt.dayofweek
                df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
            
            # Fill NaN values in rolling statistics with the value itself
            for col in df.columns:
                if col.startswith('rolling_'):
                    df[col] = df[col].fillna(df['value'])
            
            logger.info(f"Added {len([c for c in df.columns if c.startswith('rolling_')])} feature columns")
            return df
            
        except Exception as e:
            logger.error(f"Error adding feature columns: {e}")
            raise DataFormatterError(f"Failed to add features: {e}") from e
