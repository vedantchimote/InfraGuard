"""
Unit tests for PrometheusCollector.

Tests the Prometheus metrics collection functionality including
query execution, error handling, and response parsing.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.collector.prometheus_collector import PrometheusCollector


class TestPrometheusCollector:
    """Test suite for PrometheusCollector class."""
    
    @pytest.fixture
    def config(self):
        """Provide test configuration."""
        return {
            'url': 'http://prometheus:9090',
            'timeout': 30,
            'queries': [
                {
                    'name': 'cpu_usage',
                    'query': 'cpu_usage_percent',
                    'metric_type': 'cpu'
                },
                {
                    'name': 'memory_usage',
                    'query': 'memory_usage_percent',
                    'metric_type': 'memory'
                }
            ]
        }
    
    @pytest.fixture
    def collector(self, config):
        """Create PrometheusCollector instance."""
        return PrometheusCollector(config)
    
    def test_initialization(self, collector, config):
        """Test collector initializes with correct configuration."""
        assert collector.prometheus_url == 'http://prometheus:9090'
        assert collector.timeout == 30
        assert len(collector.queries) == 2
        assert collector.queries[0]['name'] == 'cpu_usage'
    
    def test_initialization_with_prometheus_url_key(self):
        """Test collector accepts prometheus_url key."""
        config = {
            'prometheus_url': 'http://localhost:9090',
            'queries': []
        }
        collector = PrometheusCollector(config)
        assert collector.prometheus_url == 'http://localhost:9090'
    
    @patch('requests.get')
    def test_execute_query_success(self, mock_get, collector):
        """Test successful query execution."""
        # Mock successful response
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
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        result = collector.execute_query('cpu_usage_percent')
        
        assert result['status'] == 'success'
        assert 'data' in result
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_execute_query_timeout(self, mock_get, collector):
        """Test query execution with timeout."""
        import requests
        mock_get.side_effect = requests.Timeout("Connection timeout")
        
        result = collector.execute_query('cpu_usage_percent')
        
        assert result is None
    
    @patch('requests.get')
    def test_execute_query_connection_error(self, mock_get, collector):
        """Test query execution with connection error."""
        import requests
        mock_get.side_effect = requests.ConnectionError("Connection refused")
        
        result = collector.execute_query('cpu_usage_percent')
        
        assert result is None
    
    @patch('requests.get')
    def test_collect_metrics_success(self, mock_get, collector):
        """Test successful metrics collection."""
        # Mock successful response
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
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        results = collector.collect_metrics()
        
        assert len(results) == 2  # Two queries configured
        assert all(r['success'] for r in results)
        assert results[0]['query_name'] == 'cpu_usage'
        assert results[1]['query_name'] == 'memory_usage'
    
    @patch('requests.get')
    def test_collect_metrics_partial_failure(self, mock_get, collector):
        """Test metrics collection with partial failures."""
        import requests
        
        # First query succeeds, second fails
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'success',
            'data': {'resultType': 'vector', 'result': []}
        }
        
        mock_get.side_effect = [
            mock_response,  # First query succeeds
            requests.Timeout("Timeout")  # Second query fails
        ]
        
        results = collector.collect_metrics()
        
        assert len(results) == 2
        assert results[0]['success'] is True
        assert results[1]['success'] is False
    
    def test_url_trailing_slash_removed(self):
        """Test that trailing slash is removed from URL."""
        config = {
            'url': 'http://prometheus:9090/',
            'queries': []
        }
        collector = PrometheusCollector(config)
        assert collector.prometheus_url == 'http://prometheus:9090'
    
    def test_empty_queries_list(self):
        """Test collector with empty queries list."""
        config = {
            'url': 'http://prometheus:9090',
            'queries': []
        }
        collector = PrometheusCollector(config)
        results = collector.collect_metrics()
        assert len(results) == 0
