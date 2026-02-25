"""
Slack notifier for InfraGuard.

This module sends formatted alert messages to Slack via webhooks
with retry logic and rich formatting.
"""

import logging
import time
import requests
from typing import Dict, Any, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


class SlackNotifierError(Exception):
    """Base exception for Slack notifier errors."""
    pass


class SlackNotifier:
    """
    Sends alert notifications to Slack.
    
    Provides formatted message delivery to Slack channels via webhooks
    with automatic retry logic and rich block formatting.
    
    Attributes:
        webhook_url: Slack webhook URL
        channel: Target Slack channel
        retry_attempts: Number of retry attempts on failure
        retry_delay: Delay between retries in seconds
    
    Example:
        >>> config = {
        ...     'webhook_url': 'https://hooks.slack.com/services/...',
        ...     'channel': '#infraguard-alerts',
        ...     'retry_attempts': 3,
        ...     'retry_delay': 10
        ... }
        >>> notifier = SlackNotifier(config)
        >>> notifier.send_anomaly_alert(anomaly_data)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Slack notifier.
        
        Args:
            config: Configuration dictionary containing:
                - webhook_url: Slack webhook URL
                - channel: Target channel (optional)
                - retry_attempts: Number of retries (default: 3)
                - retry_delay: Delay between retries in seconds (default: 10)
        
        Raises:
            ValueError: If webhook_url is missing
        """
        if 'webhook_url' not in config or not config['webhook_url']:
            raise ValueError("webhook_url is required in Slack config")
        
        self.webhook_url = config['webhook_url']
        self.channel = config.get('channel', '#infraguard-alerts')
        self.retry_attempts = config.get('retry_attempts', 3)
        self.retry_delay = config.get('retry_delay', 10)
        
        logger.info(f"Initialized SlackNotifier for channel {self.channel}")
    
    def send_message(self, payload: Dict[str, Any]) -> bool:
        """
        Send message to Slack with retry logic.
        
        Args:
            payload: Slack message payload (blocks format)
        
        Returns:
            True if message sent successfully, False otherwise
        
        Raises:
            SlackNotifierError: If all retry attempts fail
        """
        for attempt in range(1, self.retry_attempts + 1):
            try:
                logger.debug(f"Sending Slack message (attempt {attempt}/{self.retry_attempts})")
                
                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    timeout=10
                )
                response.raise_for_status()
                
                logger.info("Slack message sent successfully")
                return True
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Slack send attempt {attempt} failed: {e}")
                
                if attempt < self.retry_attempts:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"All {self.retry_attempts} Slack send attempts failed")
                    raise SlackNotifierError(f"Failed to send Slack message after {self.retry_attempts} attempts") from e
        
        return False
    
    def _get_severity_emoji(self, severity: str) -> str:
        """
        Get emoji for severity level.
        
        Args:
            severity: Severity level ('high', 'medium', 'low')
        
        Returns:
            Emoji string
        """
        emoji_map = {
            'high': ':rotating_light:',
            'medium': ':warning:',
            'low': ':information_source:'
        }
        return emoji_map.get(severity.lower(), ':bell:')
    
    def _get_severity_color(self, severity: str) -> str:
        """
        Get color for severity level.
        
        Args:
            severity: Severity level
        
        Returns:
            Hex color code
        """
        color_map = {
            'high': '#FF0000',      # Red
            'medium': '#FFA500',    # Orange
            'low': '#FFFF00'        # Yellow
        }
        return color_map.get(severity.lower(), '#808080')
    
    def _format_anomaly_message(
        self,
        metric_name: str,
        metric_value: float,
        confidence: float,
        severity: str,
        timestamp: Any,
        runbook_url: Optional[str] = None,
        jira_ticket_id: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format anomaly alert message with Slack blocks.
        
        Args:
            metric_name: Name of the metric
            metric_value: Current metric value
            confidence: Anomaly confidence percentage
            severity: Severity level
            timestamp: Timestamp of anomaly
            runbook_url: URL to runbook (optional)
            jira_ticket_id: Jira ticket ID (optional)
            additional_context: Additional context data (optional)
        
        Returns:
            Slack message payload with blocks
        """
        emoji = self._get_severity_emoji(severity)
        
        # Format timestamp
        if isinstance(timestamp, datetime):
            timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        else:
            timestamp_str = str(timestamp)
        
        # Build blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Anomaly Detected: {metric_name}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Metric:*\n{metric_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Value:*\n{metric_value:.2f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Confidence:*\n{confidence:.1f}%"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Severity:*\n{severity.upper()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Timestamp:*\n{timestamp_str}"
                    }
                ]
            }
        ]
        
        # Add Jira ticket if available
        if jira_ticket_id:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Jira Ticket:* {jira_ticket_id}"
                }
            })
        
        # Add runbook link if available
        if runbook_url:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Runbook:* <{runbook_url}|View Remediation Steps>"
                }
            })
        
        # Add additional context if provided
        if additional_context:
            context_text = "\n".join([f"*{k}:* {v}" for k, v in additional_context.items()])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Additional Context:*\n{context_text}"
                }
            })
        
        # Add divider
        blocks.append({"type": "divider"})
        
        payload = {
            "channel": self.channel,
            "blocks": blocks,
            "attachments": [
                {
                    "color": self._get_severity_color(severity),
                    "fallback": f"Anomaly detected in {metric_name}"
                }
            ]
        }
        
        return payload
    
    def _format_prediction_message(
        self,
        metric_name: str,
        predicted_value: float,
        threshold: float,
        prediction_time: Any,
        confidence_interval: Optional[tuple] = None,
        runbook_url: Optional[str] = None,
        jira_ticket_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Format forecast alert message with Slack blocks.
        
        Args:
            metric_name: Name of the metric
            predicted_value: Predicted metric value
            threshold: Threshold that will be breached
            prediction_time: Time of predicted breach
            confidence_interval: Tuple of (lower, upper) confidence bounds
            runbook_url: URL to runbook (optional)
            jira_ticket_id: Jira ticket ID (optional)
        
        Returns:
            Slack message payload with blocks
        """
        emoji = ':crystal_ball:'
        
        # Format prediction time
        if isinstance(prediction_time, datetime):
            time_str = prediction_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            time_str = str(prediction_time)
        
        # Build blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Threshold Breach Predicted: {metric_name}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Metric:*\n{metric_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Predicted Value:*\n{predicted_value:.2f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Threshold:*\n{threshold:.2f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Prediction Time:*\n{time_str}"
                    }
                ]
            }
        ]
        
        # Add confidence interval if available
        if confidence_interval:
            lower, upper = confidence_interval
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Confidence Interval:* {lower:.2f} - {upper:.2f}"
                }
            })
        
        # Add Jira ticket if available
        if jira_ticket_id:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Jira Ticket:* {jira_ticket_id}"
                }
            })
        
        # Add runbook link if available
        if runbook_url:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Runbook:* <{runbook_url}|View Preventive Actions>"
                }
            })
        
        # Add divider
        blocks.append({"type": "divider"})
        
        payload = {
            "channel": self.channel,
            "blocks": blocks,
            "attachments": [
                {
                    "color": "#FFA500",  # Orange for predictions
                    "fallback": f"Threshold breach predicted for {metric_name}"
                }
            ]
        }
        
        return payload
    
    def send_anomaly_alert(
        self,
        metric_name: str,
        metric_value: float,
        confidence: float,
        severity: str,
        timestamp: Any,
        runbook_url: Optional[str] = None,
        jira_ticket_id: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send anomaly alert to Slack.
        
        Args:
            metric_name: Name of the metric
            metric_value: Current metric value
            confidence: Anomaly confidence percentage
            severity: Severity level
            timestamp: Timestamp of anomaly
            runbook_url: URL to runbook (optional)
            jira_ticket_id: Jira ticket ID (optional)
            additional_context: Additional context data (optional)
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            payload = self._format_anomaly_message(
                metric_name, metric_value, confidence, severity,
                timestamp, runbook_url, jira_ticket_id, additional_context
            )
            return self.send_message(payload)
        except Exception as e:
            logger.error(f"Failed to send anomaly alert: {e}")
            return False
    
    def send_forecast_alert(
        self,
        metric_name: str,
        predicted_value: float,
        threshold: float,
        prediction_time: Any,
        confidence_interval: Optional[tuple] = None,
        runbook_url: Optional[str] = None,
        jira_ticket_id: Optional[str] = None
    ) -> bool:
        """
        Send forecast alert to Slack.
        
        Args:
            metric_name: Name of the metric
            predicted_value: Predicted metric value
            threshold: Threshold that will be breached
            prediction_time: Time of predicted breach
            confidence_interval: Tuple of (lower, upper) confidence bounds
            runbook_url: URL to runbook (optional)
            jira_ticket_id: Jira ticket ID (optional)
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            payload = self._format_prediction_message(
                metric_name, predicted_value, threshold, prediction_time,
                confidence_interval, runbook_url, jira_ticket_id
            )
            return self.send_message(payload)
        except Exception as e:
            logger.error(f"Failed to send forecast alert: {e}")
            return False
