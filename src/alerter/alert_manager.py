"""
Alert manager orchestration for InfraGuard.

This module coordinates alert delivery across multiple channels
(Slack, Jira) with logging and error handling.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from src.alerter.slack_notifier import SlackNotifier
from src.alerter.jira_notifier import JiraNotifier
from src.alerter.runbook_mapper import RunbookMapper


logger = logging.getLogger(__name__)


@dataclass
class AlertStatus:
    """
    Tracks alert delivery status across channels.
    
    Attributes:
        jira_success: Whether Jira ticket was created
        jira_ticket_id: Jira ticket ID if created
        slack_success: Whether Slack message was sent
        runbook_url: Runbook URL included in alert
        timestamp: When alert was sent
        error_messages: List of error messages if any
    """
    jira_success: bool
    jira_ticket_id: Optional[str]
    slack_success: bool
    runbook_url: Optional[str]
    timestamp: datetime
    error_messages: list


class AlertManager:
    """
    Orchestrates alert delivery across multiple channels.
    
    Coordinates Slack notifications, Jira ticket creation, and runbook
    resolution with comprehensive error handling and logging.
    
    Attributes:
        slack_notifier: SlackNotifier instance (optional)
        jira_notifier: JiraNotifier instance (optional)
        runbook_mapper: RunbookMapper instance
        slack_enabled: Whether Slack is enabled
        jira_enabled: Whether Jira is enabled
    
    Example:
        >>> config = {
        ...     'slack': {'enabled': True, 'webhook_url': '...'},
        ...     'jira': {'enabled': True, 'url': '...'},
        ...     'runbooks': {...}
        ... }
        >>> manager = AlertManager(config)
        >>> status = manager.send_alert(anomaly_result, 'cpu', 'high')
    """
    
    def __init__(self, alerting_config: Dict[str, Any]):
        """
        Initialize alert manager.
        
        Args:
            alerting_config: Alerting configuration dictionary containing:
                - slack: Slack configuration (optional)
                - jira: Jira configuration (optional)
                - runbooks: Runbook mappings
        """
        # Initialize Slack notifier if enabled
        slack_config = alerting_config.get('slack', {})
        self.slack_enabled = slack_config.get('enabled', False)
        self.slack_notifier = None
        
        if self.slack_enabled:
            try:
                self.slack_notifier = SlackNotifier(slack_config)
                logger.info("Slack notifications enabled")
            except Exception as e:
                logger.error(f"Failed to initialize Slack notifier: {e}")
                self.slack_enabled = False
        
        # Initialize Jira notifier if enabled
        jira_config = alerting_config.get('jira', {})
        self.jira_enabled = jira_config.get('enabled', False)
        self.jira_notifier = None
        
        if self.jira_enabled:
            try:
                self.jira_notifier = JiraNotifier(jira_config)
                logger.info("Jira integration enabled")
            except Exception as e:
                logger.error(f"Failed to initialize Jira notifier: {e}")
                self.jira_enabled = False
        
        # Initialize runbook mapper
        runbook_config = alerting_config.get('runbooks', {})
        self.runbook_mapper = RunbookMapper(runbook_config)
        
        logger.info("AlertManager initialized")
    
    def _build_alert_payload(
        self,
        metric_name: str,
        metric_value: float,
        confidence: float,
        severity: str,
        timestamp: Any,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build standardized alert payload.
        
        Args:
            metric_name: Name of the metric
            metric_value: Current metric value
            confidence: Anomaly confidence percentage
            severity: Severity level
            timestamp: Timestamp of anomaly
            additional_context: Additional context data (optional)
        
        Returns:
            Standardized alert payload dictionary
        """
        return {
            'metric_name': metric_name,
            'metric_value': metric_value,
            'confidence': confidence,
            'severity': severity,
            'timestamp': timestamp,
            'additional_context': additional_context or {}
        }
    
    def _log_alert_delivery(
        self,
        metric_name: str,
        severity: str,
        status: AlertStatus
    ) -> None:
        """
        Log alert delivery status.
        
        Args:
            metric_name: Name of the metric
            severity: Severity level
            status: AlertStatus object
        """
        log_parts = [
            f"Alert delivery for {metric_name} ({severity}):",
            f"Jira: {'✓' if status.jira_success else '✗'}",
            f"Slack: {'✓' if status.slack_success else '✗'}"
        ]
        
        if status.jira_ticket_id:
            log_parts.append(f"Ticket: {status.jira_ticket_id}")
        
        if status.runbook_url:
            log_parts.append(f"Runbook: {status.runbook_url}")
        
        if status.error_messages:
            log_parts.append(f"Errors: {', '.join(status.error_messages)}")
        
        log_message = " | ".join(log_parts)
        
        if status.error_messages:
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    def send_alert(
        self,
        metric_name: str,
        metric_value: float,
        confidence: float,
        severity: str,
        timestamp: Any,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> AlertStatus:
        """
        Send anomaly alert to all enabled channels.
        
        Sends to Jira first to get ticket ID, then includes it in Slack message.
        Handles errors gracefully and continues with other channels.
        
        Args:
            metric_name: Name of the metric
            metric_value: Current metric value
            confidence: Anomaly confidence percentage
            severity: Severity level
            timestamp: Timestamp of anomaly
            additional_context: Additional context data (optional)
        
        Returns:
            AlertStatus object with delivery results
        
        Example:
            >>> status = manager.send_alert('cpu_usage', 95.5, 92.3, 'high', datetime.now())
        """
        error_messages = []
        jira_success = False
        jira_ticket_id = None
        slack_success = False
        
        # Get runbook URL
        runbook_url = self.runbook_mapper.get_runbook(metric_name, severity)
        
        # Send to Jira first to get ticket ID
        if self.jira_enabled and self.jira_notifier:
            try:
                logger.info(f"Creating Jira ticket for {metric_name}")
                jira_ticket_id = self.jira_notifier.create_anomaly_ticket(
                    metric_name=metric_name,
                    metric_value=metric_value,
                    confidence=confidence,
                    severity=severity,
                    timestamp=timestamp,
                    runbook_url=runbook_url,
                    additional_context=additional_context
                )
                
                if jira_ticket_id:
                    jira_success = True
                    logger.info(f"Jira ticket created: {jira_ticket_id}")
                else:
                    error_messages.append("Jira ticket creation returned None")
                    
            except Exception as e:
                error_messages.append(f"Jira error: {str(e)}")
                logger.error(f"Failed to create Jira ticket: {e}")
        
        # Send to Slack with Jira ticket ID
        if self.slack_enabled and self.slack_notifier:
            try:
                logger.info(f"Sending Slack notification for {metric_name}")
                slack_success = self.slack_notifier.send_anomaly_alert(
                    metric_name=metric_name,
                    metric_value=metric_value,
                    confidence=confidence,
                    severity=severity,
                    timestamp=timestamp,
                    runbook_url=runbook_url,
                    jira_ticket_id=jira_ticket_id,
                    additional_context=additional_context
                )
                
                if slack_success:
                    logger.info("Slack notification sent successfully")
                else:
                    error_messages.append("Slack notification failed")
                    
            except Exception as e:
                error_messages.append(f"Slack error: {str(e)}")
                logger.error(f"Failed to send Slack notification: {e}")
        
        # Create status object
        status = AlertStatus(
            jira_success=jira_success,
            jira_ticket_id=jira_ticket_id,
            slack_success=slack_success,
            runbook_url=runbook_url,
            timestamp=datetime.now(),
            error_messages=error_messages
        )
        
        # Log delivery status
        self._log_alert_delivery(metric_name, severity, status)
        
        return status
    
    def send_forecast_alert(
        self,
        metric_name: str,
        predicted_value: float,
        threshold: float,
        prediction_time: Any,
        confidence_interval: Optional[tuple] = None
    ) -> AlertStatus:
        """
        Send forecast alert to all enabled channels.
        
        Sends to Jira first to get ticket ID, then includes it in Slack message.
        Handles errors gracefully and continues with other channels.
        
        Args:
            metric_name: Name of the metric
            predicted_value: Predicted metric value
            threshold: Threshold that will be breached
            prediction_time: Time of predicted breach
            confidence_interval: Tuple of (lower, upper) confidence bounds
        
        Returns:
            AlertStatus object with delivery results
        
        Example:
            >>> status = manager.send_forecast_alert('cpu_usage', 98.5, 90.0, future_time)
        """
        error_messages = []
        jira_success = False
        jira_ticket_id = None
        slack_success = False
        
        # Get runbook URL (use 'high' severity for predictions)
        runbook_url = self.runbook_mapper.get_runbook(metric_name, 'high')
        
        # Send to Jira first to get ticket ID
        if self.jira_enabled and self.jira_notifier:
            try:
                logger.info(f"Creating Jira ticket for forecast: {metric_name}")
                jira_ticket_id = self.jira_notifier.create_forecast_ticket(
                    metric_name=metric_name,
                    predicted_value=predicted_value,
                    threshold=threshold,
                    prediction_time=prediction_time,
                    confidence_interval=confidence_interval,
                    runbook_url=runbook_url
                )
                
                if jira_ticket_id:
                    jira_success = True
                    logger.info(f"Jira ticket created: {jira_ticket_id}")
                else:
                    error_messages.append("Jira ticket creation returned None")
                    
            except Exception as e:
                error_messages.append(f"Jira error: {str(e)}")
                logger.error(f"Failed to create Jira ticket: {e}")
        
        # Send to Slack with Jira ticket ID
        if self.slack_enabled and self.slack_notifier:
            try:
                logger.info(f"Sending Slack forecast notification for {metric_name}")
                slack_success = self.slack_notifier.send_forecast_alert(
                    metric_name=metric_name,
                    predicted_value=predicted_value,
                    threshold=threshold,
                    prediction_time=prediction_time,
                    confidence_interval=confidence_interval,
                    runbook_url=runbook_url,
                    jira_ticket_id=jira_ticket_id
                )
                
                if slack_success:
                    logger.info("Slack forecast notification sent successfully")
                else:
                    error_messages.append("Slack notification failed")
                    
            except Exception as e:
                error_messages.append(f"Slack error: {str(e)}")
                logger.error(f"Failed to send Slack notification: {e}")
        
        # Create status object
        status = AlertStatus(
            jira_success=jira_success,
            jira_ticket_id=jira_ticket_id,
            slack_success=slack_success,
            runbook_url=runbook_url,
            timestamp=datetime.now(),
            error_messages=error_messages
        )
        
        # Log delivery status
        self._log_alert_delivery(metric_name, 'forecast', status)
        
        return status
