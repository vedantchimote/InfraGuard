"""
Runbook mapper for InfraGuard.

This module maps metrics and anomaly types to runbook URLs for
remediation guidance.
"""

import logging
from typing import Dict, Any, Optional


logger = logging.getLogger(__name__)


class RunbookMapper:
    """
    Maps metrics and anomaly severity to runbook URLs.
    
    Provides runbook URL resolution with fallback logic for
    operational guidance during incidents.
    
    Attributes:
        runbook_mappings: Dictionary of metric -> severity -> URL mappings
        default_url: Default runbook URL when no specific mapping exists
    
    Example:
        >>> config = {
        ...     'cpu': {
        ...         'high': 'https://runbooks.example.com/cpu-spike',
        ...         'medium': 'https://runbooks.example.com/cpu-elevated'
        ...     },
        ...     'default': 'https://runbooks.example.com/general'
        ... }
        >>> mapper = RunbookMapper(config)
        >>> url = mapper.get_runbook('cpu', 'high')
    """
    
    def __init__(self, runbook_config: Dict[str, Any]):
        """
        Initialize runbook mapper with configuration.
        
        Args:
            runbook_config: Dictionary mapping metrics to severity levels to URLs
                Format: {
                    'metric_type': {
                        'high': 'url',
                        'medium': 'url'
                    },
                    'default': 'default_url'
                }
        """
        self.runbook_mappings = runbook_config.copy()
        self.default_url = self.runbook_mappings.pop('default', None)
        
        logger.info(f"Initialized RunbookMapper with {len(self.runbook_mappings)} metric mappings")
        if self.default_url:
            logger.info(f"Default runbook URL: {self.default_url}")
    
    def get_runbook(
        self,
        metric_type: str,
        severity: Optional[str] = None
    ) -> Optional[str]:
        """
        Get runbook URL for metric and severity level.
        
        Resolution order:
        1. Specific metric + severity mapping
        2. Metric mapping (any severity)
        3. Default URL
        4. None
        
        Args:
            metric_type: Type of metric (e.g., 'cpu', 'memory', 'error_rate')
            severity: Severity level ('high', 'medium', 'low') or None
        
        Returns:
            Runbook URL or None if no mapping found
        
        Example:
            >>> url = mapper.get_runbook('cpu', 'high')
            >>> url = mapper.get_runbook('unknown_metric')  # Returns default
        """
        # Normalize metric type (remove _usage, _percent suffixes)
        normalized_metric = self._normalize_metric_type(metric_type)
        
        # Try specific metric + severity
        if normalized_metric in self.runbook_mappings:
            metric_mappings = self.runbook_mappings[normalized_metric]
            
            if isinstance(metric_mappings, dict) and severity:
                # Try exact severity match
                if severity in metric_mappings:
                    url = metric_mappings[severity]
                    logger.debug(f"Found runbook for {normalized_metric}/{severity}: {url}")
                    return url
                
                # Try lowercase severity
                severity_lower = severity.lower()
                if severity_lower in metric_mappings:
                    url = metric_mappings[severity_lower]
                    logger.debug(f"Found runbook for {normalized_metric}/{severity_lower}: {url}")
                    return url
                
                # Return first available severity mapping
                if metric_mappings:
                    url = next(iter(metric_mappings.values()))
                    logger.debug(f"Using first available runbook for {normalized_metric}: {url}")
                    return url
            
            elif isinstance(metric_mappings, str):
                # Direct URL mapping
                logger.debug(f"Found direct runbook for {normalized_metric}: {metric_mappings}")
                return metric_mappings
        
        # Fallback to default
        if self.default_url:
            logger.debug(f"Using default runbook for {normalized_metric}: {self.default_url}")
            return self.default_url
        
        logger.warning(f"No runbook found for {normalized_metric}/{severity}")
        return None
    
    def _normalize_metric_type(self, metric_type: str) -> str:
        """
        Normalize metric type for consistent lookup.
        
        Removes common suffixes like _usage, _percent, _rate.
        
        Args:
            metric_type: Original metric type
        
        Returns:
            Normalized metric type
        
        Example:
            >>> mapper._normalize_metric_type('cpu_usage')
            'cpu'
            >>> mapper._normalize_metric_type('http_error_rate')
            'error_rate'
        """
        # Remove common suffixes
        suffixes = ['_usage', '_percent', '_percentage', '_ms', '_seconds']
        normalized = metric_type.lower()
        
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)]
                break
        
        return normalized
    
    def get_all_runbooks(self) -> Dict[str, Any]:
        """
        Get all configured runbook mappings.
        
        Returns:
            Dictionary of all runbook mappings
        
        Example:
            >>> all_runbooks = mapper.get_all_runbooks()
            >>> print(all_runbooks.keys())
        """
        return self.runbook_mappings.copy()
    
    def has_runbook(self, metric_type: str, severity: Optional[str] = None) -> bool:
        """
        Check if runbook exists for metric and severity.
        
        Args:
            metric_type: Type of metric
            severity: Severity level (optional)
        
        Returns:
            True if runbook exists, False otherwise
        
        Example:
            >>> if mapper.has_runbook('cpu', 'high'):
            ...     url = mapper.get_runbook('cpu', 'high')
        """
        return self.get_runbook(metric_type, severity) is not None
