"""
Jira notifier for InfraGuard.

This module creates Jira tickets for anomalies and predictions
via the Jira REST API.
"""

import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


class JiraNotifierError(Exception):
    """Base exception for Jira notifier errors."""
    pass


class JiraNotifier:
    """
    Creates Jira tickets for alerts.
    
    Provides ticket creation via Jira REST API v3 with HTTP Basic Auth
    and priority mapping based on severity.
    
    Attributes:
        api_url: Jira API base URL
        project_key: Jira project key
        username: Jira username/email
        api_token: Jira API token
    
    Example:
        >>> config = {
        ...     'url': 'https://your-domain.atlassian.net',
        ...     'project_key': 'INFRA',
        ...     'username': 'user@example.com',
        ...     'api_token': 'your-api-token'
        ... }
        >>> notifier = JiraNotifier(config)
        >>> ticket_id = notifier.create_anomaly_ticket(anomaly_data)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Jira notifier.
        
        Args:
            config: Configuration dictionary containing:
                - url: Jira instance URL
                - project_key: Jira project key
                - username: Jira username/email
                - api_token: Jira API token
        
        Raises:
            ValueError: If required configuration is missing
        """
        required_fields = ['url', 'project_key', 'username', 'api_token']
        for field in required_fields:
            if field not in config or not config[field]:
                raise ValueError(f"{field} is required in Jira config")
        
        self.api_url = config['url'].rstrip('/') + '/rest/api/3'
        self.project_key = config['project_key']
        self.username = config['username']
        self.api_token = config['api_token']
        
        logger.info(f"Initialized JiraNotifier for project {self.project_key}")
    
    def _get_priority_from_severity(self, severity: str) -> str:
        """
        Map severity level to Jira priority.
        
        Args:
            severity: Severity level ('high', 'medium', 'low')
        
        Returns:
            Jira priority name
        """
        priority_map = {
            'high': 'Highest',
            'medium': 'High',
            'low': 'Medium'
        }
        return priority_map.get(severity.lower(), 'Medium')
    
    def _format_anomaly_ticket(
        self,
        metric_name: str,
        metric_value: float,
        confidence: float,
        severity: str,
        timestamp: Any,
        runbook_url: Optional[str] = None,
        prometheus_url: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format Jira ticket payload for anomaly.
        
        Args:
            metric_name: Name of the metric
            metric_value: Current metric value
            confidence: Anomaly confidence percentage
            severity: Severity level
            timestamp: Timestamp of anomaly
            runbook_url: URL to runbook (optional)
            prometheus_url: URL to Prometheus graph (optional)
            additional_context: Additional context data (optional)
        
        Returns:
            Jira API payload dictionary
        """
        # Format timestamp
        if isinstance(timestamp, datetime):
            timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        else:
            timestamp_str = str(timestamp)
        
        # Build description
        description_parts = [
            f"*Anomaly Detected in {metric_name}*",
            "",
            f"*Metric:* {metric_name}",
            f"*Current Value:* {metric_value:.2f}",
            f"*Confidence:* {confidence:.1f}%",
            f"*Severity:* {severity.upper()}",
            f"*Timestamp:* {timestamp_str}",
            ""
        ]
        
        # Add runbook link
        if runbook_url:
            description_parts.extend([
                "*Remediation Steps:*",
                f"See runbook: {runbook_url}",
                ""
            ])
        
        # Add Prometheus link
        if prometheus_url:
            description_parts.extend([
                "*Prometheus Graph:*",
                prometheus_url,
                ""
            ])
        
        # Add additional context
        if additional_context:
            description_parts.append("*Additional Context:*")
            for key, value in additional_context.items():
                description_parts.append(f"- {key}: {value}")
            description_parts.append("")
        
        description_parts.extend([
            "---",
            "_This ticket was automatically created by InfraGuard AIOps._"
        ])
        
        description = "\n".join(description_parts)
        
        # Build payload
        payload = {
            "fields": {
                "project": {
                    "key": self.project_key
                },
                "summary": f"[InfraGuard] Anomaly in {metric_name} - {severity.upper()} severity",
                "description": description,
                "issuetype": {
                    "name": "Bug"
                },
                "priority": {
                    "name": self._get_priority_from_severity(severity)
                },
                "labels": [
                    "infraguard",
                    "anomaly",
                    f"severity-{severity.lower()}",
                    f"metric-{metric_name.replace('_', '-')}"
                ]
            }
        }
        
        return payload
    
    def _format_prediction_ticket(
        self,
        metric_name: str,
        predicted_value: float,
        threshold: float,
        prediction_time: Any,
        confidence_interval: Optional[tuple] = None,
        runbook_url: Optional[str] = None,
        prometheus_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Format Jira ticket payload for forecast alert.
        
        Args:
            metric_name: Name of the metric
            predicted_value: Predicted metric value
            threshold: Threshold that will be breached
            prediction_time: Time of predicted breach
            confidence_interval: Tuple of (lower, upper) confidence bounds
            runbook_url: URL to runbook (optional)
            prometheus_url: URL to Prometheus graph (optional)
        
        Returns:
            Jira API payload dictionary
        """
        # Format prediction time
        if isinstance(prediction_time, datetime):
            time_str = prediction_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            time_str = str(prediction_time)
        
        # Build description
        description_parts = [
            f"*Threshold Breach Predicted for {metric_name}*",
            "",
            f"*Metric:* {metric_name}",
            f"*Predicted Value:* {predicted_value:.2f}",
            f"*Threshold:* {threshold:.2f}",
            f"*Prediction Time:* {time_str}",
            ""
        ]
        
        # Add confidence interval
        if confidence_interval:
            lower, upper = confidence_interval
            description_parts.extend([
                f"*Confidence Interval:* {lower:.2f} - {upper:.2f}",
                ""
            ])
        
        # Add runbook link
        if runbook_url:
            description_parts.extend([
                "*Preventive Actions:*",
                f"See runbook: {runbook_url}",
                ""
            ])
        
        # Add Prometheus link
        if prometheus_url:
            description_parts.extend([
                "*Prometheus Graph:*",
                prometheus_url,
                ""
            ])
        
        description_parts.extend([
            "---",
            "_This ticket was automatically created by InfraGuard AIOps based on time-series forecasting._"
        ])
        
        description = "\n".join(description_parts)
        
        # Build payload
        payload = {
            "fields": {
                "project": {
                    "key": self.project_key
                },
                "summary": f"[InfraGuard] Predicted threshold breach for {metric_name}",
                "description": description,
                "issuetype": {
                    "name": "Task"
                },
                "priority": {
                    "name": "High"
                },
                "labels": [
                    "infraguard",
                    "prediction",
                    "forecast",
                    f"metric-{metric_name.replace('_', '-')}"
                ]
            }
        }
        
        return payload
    
    def create_ticket(self, payload: Dict[str, Any]) -> Optional[str]:
        """
        Create Jira ticket via REST API.
        
        Args:
            payload: Jira API payload
        
        Returns:
            Jira ticket ID (e.g., 'INFRA-123') or None if creation fails
        
        Raises:
            JiraNotifierError: If ticket creation fails
        """
        try:
            url = f"{self.api_url}/issue"
            
            logger.debug(f"Creating Jira ticket in project {self.project_key}")
            
            response = requests.post(
                url,
                json=payload,
                auth=(self.username, self.api_token),
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            ticket_key = data.get('key')
            
            if ticket_key:
                logger.info(f"Created Jira ticket: {ticket_key}")
                return ticket_key
            else:
                logger.error("Jira API response missing ticket key")
                return None
                
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(f"Failed to create Jira ticket: {error_msg}")
            raise JiraNotifierError(f"Failed to create ticket: {error_msg}") from e
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error creating Jira ticket: {e}")
            raise JiraNotifierError(f"Failed to create ticket: {e}") from e
    
    def create_anomaly_ticket(
        self,
        metric_name: str,
        metric_value: float,
        confidence: float,
        severity: str,
        timestamp: Any,
        runbook_url: Optional[str] = None,
        prometheus_url: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create Jira ticket for anomaly alert.
        
        Args:
            metric_name: Name of the metric
            metric_value: Current metric value
            confidence: Anomaly confidence percentage
            severity: Severity level
            timestamp: Timestamp of anomaly
            runbook_url: URL to runbook (optional)
            prometheus_url: URL to Prometheus graph (optional)
            additional_context: Additional context data (optional)
        
        Returns:
            Jira ticket ID or None if creation fails
        """
        try:
            payload = self._format_anomaly_ticket(
                metric_name, metric_value, confidence, severity,
                timestamp, runbook_url, prometheus_url, additional_context
            )
            return self.create_ticket(payload)
        except Exception as e:
            logger.error(f"Failed to create anomaly ticket: {e}")
            return None
    
    def create_forecast_ticket(
        self,
        metric_name: str,
        predicted_value: float,
        threshold: float,
        prediction_time: Any,
        confidence_interval: Optional[tuple] = None,
        runbook_url: Optional[str] = None,
        prometheus_url: Optional[str] = None
    ) -> Optional[str]:
        """
        Create Jira ticket for forecast alert.
        
        Args:
            metric_name: Name of the metric
            predicted_value: Predicted metric value
            threshold: Threshold that will be breached
            prediction_time: Time of predicted breach
            confidence_interval: Tuple of (lower, upper) confidence bounds
            runbook_url: URL to runbook (optional)
            prometheus_url: URL to Prometheus graph (optional)
        
        Returns:
            Jira ticket ID or None if creation fails
        """
        try:
            payload = self._format_prediction_ticket(
                metric_name, predicted_value, threshold, prediction_time,
                confidence_interval, runbook_url, prometheus_url
            )
            return self.create_ticket(payload)
        except Exception as e:
            logger.error(f"Failed to create forecast ticket: {e}")
            return None
