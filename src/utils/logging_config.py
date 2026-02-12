"""
Logging configuration for InfraGuard.

This module provides centralized logging setup with support for
file and console output, configurable log levels, and structured formatting.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_format: Optional[str] = None,
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Configure application-wide logging.
    
    Sets up logging with both console and file handlers. File handler uses
    rotating file handler to prevent unbounded log growth.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Custom log format string (uses default if None)
        log_file: Path to log file (logs to console only if None)
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
    
    Example:
        >>> setup_logging(log_level="DEBUG", log_file="logs/infraguard.log")
        >>> logger = logging.getLogger(__name__)
        >>> logger.info("Application started")
    """
    # Default format includes timestamp, logger name, level, and message
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (rotating) if log file specified
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Log initial message
    root_logger.info(f"Logging initialized at {log_level} level")
    if log_file:
        root_logger.info(f"Logging to file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__ of the calling module)
    
    Returns:
        Configured logger instance
    
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing metrics")
    """
    return logging.getLogger(name)
