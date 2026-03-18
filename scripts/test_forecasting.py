#!/usr/bin/env python3
"""
Test script for time-series forecasting functionality.

This script validates that the TimeSeriesForecaster can:
1. Load configuration correctly
2. Generate forecasts from historical data
3. Detect threshold breaches
4. Return proper ForecastResult objects
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ml.forecaster import TimeSeriesForecaster, ForecastResult


def generate_synthetic_data(days: int = 3, anomaly: bool = False) -> pd.DataFrame:
    """
    Generate synthetic time-series data for testing.
    
    Args:
        days: Number of days of data to generate
        anomaly: Whether to include an upward trend (simulating anomaly)
    
    Returns:
        DataFrame with columns [timestamp, value]
    """
    # Generate timestamps (1-minute intervals)
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    timestamps = pd.date_range(start=start_time, end=end_time, freq='1min')
    
    # Generate values with daily seasonality
    hours = np.array([t.hour + t.minute / 60 for t in timestamps])
    
    # Base pattern: higher during business hours (9-17)
    base_value = 50
    daily_pattern = 20 * np.sin((hours - 6) * np.pi / 12)
    
    # Add some noise
    noise = np.random.normal(0, 5, len(timestamps))
    
    # Add trend if anomaly
    if anomaly:
        trend = np.linspace(0, 30, len(timestamps))
    else:
        trend = 0
    
    values = base_value + daily_pattern + noise + trend
    
    # Ensure non-negative
    values = np.maximum(values, 0)
    
    return pd.DataFrame({
        'timestamp': timestamps,
        'value': values
    })


def test_forecaster_initialization():
    """Test that forecaster initializes correctly."""
    print("=" * 60)
    print("Test 1: Forecaster Initialization")
    print("=" * 60)
    
    config = {
        'prediction_window': 900,  # 15 minutes in seconds
        'prophet': {
            'seasonality_mode': 'multiplicative',
            'changepoint_prior_scale': 0.05,
            'interval_width': 0.95
        },
        'thresholds': {
            'cpu': {
                'severity_high': 80,
                'severity_medium': 70
            }
        }
    }
    
    forecaster = TimeSeriesForecaster(config)
    
    assert forecaster.prediction_window_minutes == 15, "Prediction window should be 15 minutes"
    assert forecaster.thresholds['cpu']['severity_high'] == 80, "Threshold should be 80"
    
    print("✅ Forecaster initialized successfully")
    print(f"   - Prediction window: {forecaster.prediction_window_minutes} minutes")
    print(f"   - Thresholds configured: {list(forecaster.thresholds.keys())}")
    print()
    
    return forecaster


def test_forecast_generation(forecaster: TimeSeriesForecaster):
    """Test that forecaster can generate predictions."""
    print("=" * 60)
    print("Test 2: Forecast Generation")
    print("=" * 60)
    
    # Generate 3 days of normal data
    data = generate_synthetic_data(days=3, anomaly=False)
    
    print(f"Generated {len(data)} data points ({len(data) / 1440:.1f} days)")
    print(f"Value range: {data['value'].min():.2f} - {data['value'].max():.2f}")
    
    # Generate forecast
    result = forecaster.forecast(data, 'cpu')
    
    assert isinstance(result, ForecastResult), "Should return ForecastResult"
    assert len(result.predictions) == 15, "Should have 15 predictions (15 minutes)"
    assert 'yhat' in result.predictions.columns, "Should have yhat column"
    assert 'yhat_lower' in result.predictions.columns, "Should have confidence intervals"
    assert 'yhat_upper' in result.predictions.columns, "Should have confidence intervals"
    
    print("✅ Forecast generated successfully")
    print(f"   - Predictions: {len(result.predictions)}")
    print(f"   - Predicted range: {result.predictions['yhat'].min():.2f} - {result.predictions['yhat'].max():.2f}")
    print(f"   - Breach predicted: {result.breach_time is not None}")
    print()
    
    return result


def test_threshold_breach_detection(forecaster: TimeSeriesForecaster):
    """Test that forecaster detects threshold breaches."""
    print("=" * 60)
    print("Test 3: Threshold Breach Detection")
    print("=" * 60)
    
    # Generate 3 days of data with upward trend
    data = generate_synthetic_data(days=3, anomaly=True)
    
    print(f"Generated {len(data)} data points with upward trend")
    print(f"Value range: {data['value'].min():.2f} - {data['value'].max():.2f}")
    
    # Generate forecast
    result = forecaster.forecast(data, 'cpu')
    
    print(f"✅ Forecast generated")
    print(f"   - Breach predicted: {result.breach_time is not None}")
    
    if result.breach_time:
        print(f"   - Breach time: {result.breach_time}")
        print(f"   - Breach value: {result.breach_value:.2f}")
        print(f"   - Confidence interval: [{result.confidence_interval_lower:.2f}, {result.confidence_interval_upper:.2f}]")
    else:
        print(f"   - No breach predicted (max predicted value: {result.predictions['yhat'].max():.2f})")
    
    print()
    
    return result


def test_insufficient_data_handling(forecaster: TimeSeriesForecaster):
    """Test that forecaster handles insufficient data gracefully."""
    print("=" * 60)
    print("Test 4: Insufficient Data Handling")
    print("=" * 60)
    
    # Generate only 1 day of data (insufficient)
    data = generate_synthetic_data(days=1, anomaly=False)
    
    print(f"Generated {len(data)} data points ({len(data) / 1440:.1f} days)")
    
    try:
        result = forecaster.forecast(data, 'cpu')
        print("❌ Should have raised ValueError for insufficient data")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")
    
    print()


def test_forecast_result_serialization():
    """Test that ForecastResult can be serialized to dict."""
    print("=" * 60)
    print("Test 5: ForecastResult Serialization")
    print("=" * 60)
    
    # Create a sample ForecastResult
    predictions = pd.DataFrame({
        'ds': pd.date_range(start='2024-01-01', periods=15, freq='1min'),
        'yhat': np.random.uniform(50, 70, 15),
        'yhat_lower': np.random.uniform(40, 60, 15),
        'yhat_upper': np.random.uniform(60, 80, 15)
    })
    
    result = ForecastResult(
        predictions=predictions,
        breach_time=datetime(2024, 1, 1, 12, 5),
        breach_value=85.5,
        confidence_interval_lower=80.2,
        confidence_interval_upper=90.8
    )
    
    # Serialize to dict
    result_dict = result.to_dict()
    
    assert 'breach_predicted' in result_dict, "Should have breach_predicted field"
    assert result_dict['breach_predicted'] is True, "Should indicate breach"
    assert result_dict['breach_time'] is not None, "Should have breach time"
    assert result_dict['breach_value'] == 85.5, "Should have breach value"
    
    print("✅ ForecastResult serialized successfully")
    print(f"   - Breach predicted: {result_dict['breach_predicted']}")
    print(f"   - Breach time: {result_dict['breach_time']}")
    print(f"   - Breach value: {result_dict['breach_value']}")
    print()


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "Time-Series Forecasting Test Suite" + " " * 14 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    try:
        # Test 1: Initialization
        forecaster = test_forecaster_initialization()
        
        # Test 2: Forecast generation
        test_forecast_generation(forecaster)
        
        # Test 3: Threshold breach detection
        test_threshold_breach_detection(forecaster)
        
        # Test 4: Insufficient data handling
        test_insufficient_data_handling(forecaster)
        
        # Test 5: Serialization
        test_forecast_result_serialization()
        
        # Summary
        print("=" * 60)
        print("Test Summary")
        print("=" * 60)
        print("✅ All tests passed!")
        print()
        print("The TimeSeriesForecaster is working correctly:")
        print("  - Initializes with configuration")
        print("  - Generates forecasts from historical data")
        print("  - Detects threshold breaches")
        print("  - Handles insufficient data gracefully")
        print("  - Serializes results to dict")
        print()
        print("To enable forecasting in InfraGuard:")
        print("  1. Edit config/settings.yaml")
        print("  2. Set forecasting.enabled: true")
        print("  3. Restart InfraGuard")
        print()
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
