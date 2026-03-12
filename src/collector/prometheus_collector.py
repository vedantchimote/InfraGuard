"""
Prometheus metrics collector for InfraGuard.

This module provides functionality to query Prometheus for metrics data
and handle connection errors gracefully.
"""

import logging
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class PrometheusQuery:
    """Represents a Prometheus query configuration."""
    name: str
    query: str
    metric_type: str


class PrometheusCollectorError(Exception):
    """Base exception for Prometheus collector errors."""
    pass


class PrometheusConnectionError(PrometheusCollectorError):
    """Raised when connection to Prometheus fails."""
    pass


class PrometheusQueryError(PrometheusCollectorError):
    """Raised when query execution fails."""
    pass


class PrometheusCollector:
    """
    Collects metrics from Prometheus using PromQL queries.
    
    This class handles HTTP communication with Prometheus, executes configured
    queries, and manages connection errors and timeouts.
    
    Attributes:
        prometheus_url: Base URL of Prometheus server
        queries: List of PrometheusQuery objects to execute
        timeout: HTTP request timeout in seconds
    
    Example:
        >>> config = {
        ...     'prometheus_url': 'http://localhost:9090',
        ...     'queries': [
        ...         {'name': 'cpu', 'query': 'rate(cpu_usage[5m])', 'metric_type': 'cpu'}
        ...     ],
        ...     'timeout': 30
        ... }
        >>> collector = PrometheusCollector(config)
        >>> results = collector.collect_metrics()
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Prometheus collector with configuration.
        
        Args:
            config: Configuration dictionary containing:
                - prometheus_url: Prometheus server URL
                - queries: List of query configurations
                - timeout: Request timeout in seconds (default: 30)
        
        Raises:
            ValueError: If required configuration is missing
        """
        if 'prometheus_url' not in config and 'url' not in config:
            raise ValueError("prometheus_url or url is required in config")
        if 'queries' not in config or not config['queries']:
            raise ValueError("queries list is required in config")
        
        self.prometheus_url = config.get('prometheus_url', config.get('url', '')).rstrip('/')
        self.timeout = config.get('timeout', 30)
        
        # Parse queries into PrometheusQuery objects
        self.queries: List[PrometheusQuery] = []
        for q in config['queries']:
            if 'name' not in q or 'query' not in q:
                logger.warning(f"Skipping invalid query config: {q}")
                continue
            self.queries.append(PrometheusQuery(
                name=q['name'],
                query=q['query'],
                metric_type=q.get('metric_type', 'unknown')
            ))
        
        logger.info(f"Initialized PrometheusCollector with {len(self.queries)} queries")
    
    def execute_query(self, query: str) -> Dict[str, Any]:
        """
        Execute a single PromQL query via HTTP GET.
        
        Args:
            query: PromQL query string
        
        Returns:
            Dictionary containing Prometheus API response
        
        Raises:
            PrometheusConnectionError: If connection fails or times out
            PrometheusQueryError: If query execution fails
        """
        url = f"{self.prometheus_url}/api/v1/query"
        params = {'query': query}
        
        try:
            logger.debug(f"Executing query: {query}")
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Check Prometheus API status
            if data.get('status') != 'success':
                error_msg = data.get('error', 'Unknown error')
                raise PrometheusQueryError(f"Query failed: {error_msg}")
            
            logger.debug(f"Query executed successfully, returned {len(data.get('data', {}).get('result', []))} results")
            return data
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout querying Prometheus: {e}")
            raise PrometheusConnectionError(f"Request timed out after {self.timeout}s") from e
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error to Prometheus: {e}")
            raise PrometheusConnectionError(f"Failed to connect to {self.prometheus_url}") from e
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error from Prometheus: {e}")
            raise PrometheusQueryError(f"HTTP {e.response.status_code}: {e}") from e
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise PrometheusConnectionError(f"Request failed: {e}") from e
    
    def collect_metrics(self) -> List[Dict[str, Any]]:
        """
        Execute all configured queries and collect results.
        
        Returns:
            List of dictionaries, each containing:
                - query_name: Name of the query
                - metric_type: Type of metric
                - data: Prometheus API response data
                - success: Boolean indicating if query succeeded
                - error: Error message if query failed (optional)
        
        Example:
            >>> results = collector.collect_metrics()
            >>> for result in results:
            ...     if result['success']:
            ...         print(f"Collected {result['query_name']}")
        """
        results = []
        
        for prom_query in self.queries:
            result = {
                'query_name': prom_query.name,
                'metric_type': prom_query.metric_type,
                'success': False
            }
            
            try:
                data = self.execute_query(prom_query.query)
                result['data'] = data
                result['success'] = True
                logger.info(f"Successfully collected metrics for query: {prom_query.name}")
                
            except PrometheusCollectorError as e:
                result['error'] = str(e)
                logger.error(f"Failed to collect metrics for query {prom_query.name}: {e}")
            
            results.append(result)
        
        successful_count = sum(1 for r in results if r['success'])
        logger.info(f"Collected metrics: {successful_count}/{len(results)} queries succeeded")
        
        return results
