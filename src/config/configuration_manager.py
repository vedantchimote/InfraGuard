"""
Configuration management for InfraGuard.

This module provides centralized configuration loading, validation,
and access with support for environment variable substitution.
"""

import os
import yaml
import logging
from typing import Any, Dict, Optional
from pathlib import Path


logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Base exception for configuration errors."""
    pass


class ConfigurationManager:
    """
    Manages application configuration from YAML files.
    
    Loads configuration from YAML files, validates required fields,
    and provides convenient access methods with dot-notation support.
    Supports environment variable substitution in configuration values.
    
    Attributes:
        config: Dictionary containing the loaded configuration
        config_path: Path to the configuration file
    
    Example:
        >>> config_mgr = ConfigurationManager('config/settings.yaml')
        >>> prometheus_url = config_mgr.get('prometheus.url')
        >>> queries = config_mgr.get_prometheus_config()['queries']
    """
    
    def __init__(self, config_path: str):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to YAML configuration file
        
        Raises:
            ConfigurationError: If config file doesn't exist or is invalid
        """
        self.config_path = Path(config_path)
        
        if not self.config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        
        self.config = self._load_config()
        self._validate_config()
        
        logger.info(f"Configuration loaded from {config_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Performs environment variable substitution for values in the format:
        ${ENV_VAR_NAME} or ${ENV_VAR_NAME:default_value}
        
        Returns:
            Dictionary containing configuration
        
        Raises:
            ConfigurationError: If file cannot be read or parsed
        """
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if config is None:
                raise ConfigurationError("Configuration file is empty")
            
            # Perform environment variable substitution
            config = self._substitute_env_vars(config)
            
            return config
            
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML syntax: {e}") from e
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}") from e
    
    def _substitute_env_vars(self, obj: Any) -> Any:
        """
        Recursively substitute environment variables in configuration.
        
        Supports syntax: ${VAR_NAME} or ${VAR_NAME:default_value}
        
        Args:
            obj: Configuration object (dict, list, str, or other)
        
        Returns:
            Object with environment variables substituted
        """
        if isinstance(obj, dict):
            return {k: self._substitute_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            # Check for environment variable pattern
            if obj.startswith('${') and obj.endswith('}'):
                var_expr = obj[2:-1]  # Remove ${ and }
                
                # Check for default value syntax
                if ':' in var_expr:
                    var_name, default_value = var_expr.split(':', 1)
                    return os.getenv(var_name, default_value)
                else:
                    # Use the original value as default if env var not set
                    return os.getenv(var_expr, obj)
            
            # Also handle inline substitution
            import re
            pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'
            
            def replace_match(match):
                var_name = match.group(1)
                default_value = match.group(2) if match.group(2) is not None else match.group(0)
                return os.getenv(var_name, default_value)
            
            return re.sub(pattern, replace_match, obj)
        else:
            return obj
    
    def _validate_config(self) -> None:
        """
        Validate that required configuration fields are present.
        
        Raises:
            ConfigurationError: If required fields are missing
        """
        required_sections = ['prometheus', 'collection', 'ml', 'logging']
        
        for section in required_sections:
            if section not in self.config:
                raise ConfigurationError(f"Required configuration section missing: {section}")
        
        # Validate Prometheus configuration
        prometheus_config = self.config['prometheus']
        if 'url' not in prometheus_config:
            raise ConfigurationError("prometheus.url is required")
        if 'queries' not in prometheus_config or not prometheus_config['queries']:
            raise ConfigurationError("prometheus.queries is required and must not be empty")
        
        # Validate ML configuration
        ml_config = self.config['ml']
        if 'isolation_forest' not in ml_config:
            raise ConfigurationError("ml.isolation_forest configuration is required")
        if 'model_path' not in ml_config:
            raise ConfigurationError("ml.model_path is required")
        
        # Validate collection configuration
        collection_config = self.config['collection']
        if 'interval' not in collection_config:
            raise ConfigurationError("collection.interval is required")
        
        logger.debug("Configuration validation passed")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key in dot notation (e.g., 'prometheus.url')
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        
        Example:
            >>> config_mgr.get('prometheus.url')
            'http://localhost:9090'
            >>> config_mgr.get('ml.isolation_forest.n_estimators', 100)
            100
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_prometheus_config(self) -> Dict[str, Any]:
        """
        Get Prometheus-specific configuration.
        
        Returns:
            Dictionary containing Prometheus configuration
        """
        return self.config.get('prometheus', {})
    
    def get_ml_config(self) -> Dict[str, Any]:
        """
        Get machine learning configuration.
        
        Returns:
            Dictionary containing ML configuration
        """
        return self.config.get('ml', {})
    
    def get_collection_config(self) -> Dict[str, Any]:
        """
        Get collection configuration.
        
        Returns:
            Dictionary containing collection configuration
        """
        return self.config.get('collection', {})
    
    def get_alerting_config(self) -> Dict[str, Any]:
        """
        Get alerting configuration.
        
        Returns:
            Dictionary containing alerting configuration
        """
        return self.config.get('alerting', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """
        Get logging configuration.
        
        Returns:
            Dictionary containing logging configuration
        """
        return self.config.get('logging', {})
    
    def get_forecasting_config(self) -> Dict[str, Any]:
        """
        Get forecasting configuration.
        
        Returns:
            Dictionary containing forecasting configuration
        """
        return self.config.get('forecasting', {})
    
    def is_forecasting_enabled(self) -> bool:
        """
        Check if time-series forecasting is enabled.
        
        Returns:
            True if forecasting is enabled, False otherwise
        """
        return self.get('forecasting.enabled', False)
    
    def is_slack_enabled(self) -> bool:
        """
        Check if Slack notifications are enabled.
        
        Returns:
            True if Slack is enabled, False otherwise
        """
        return self.get('alerting.slack.enabled', False)
    
    def is_jira_enabled(self) -> bool:
        """
        Check if Jira integration is enabled.
        
        Returns:
            True if Jira is enabled, False otherwise
        """
        return self.get('alerting.jira.enabled', False)
