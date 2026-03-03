#!/usr/bin/env python3
"""
InfraGuard AIOps - Main entry point.

AI-powered infrastructure monitoring with anomaly detection and alerting.
"""

import sys
import argparse
from pathlib import Path

from src.infraguard import InfraGuard
from src.config.configuration_manager import ConfigurationError


def main():
    """Main entry point for InfraGuard application."""
    parser = argparse.ArgumentParser(
        description='InfraGuard AIOps - AI-powered infrastructure monitoring',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default config
  python main.py

  # Run with custom config
  python main.py --config /path/to/settings.yaml

  # Run with custom log level
  python main.py --log-level DEBUG

For more information, visit: https://github.com/your-org/infraguard
        """
    )
    
    parser.add_argument(
        '--config',
        default='config/settings.yaml',
        help='Path to configuration file (default: config/settings.yaml)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Override log level from config'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='InfraGuard 0.1.0'
    )
    
    args = parser.parse_args()
    
    # Check if config file exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Configuration file not found: {args.config}", file=sys.stderr)
        print(f"Please create a configuration file or specify a valid path with --config", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Initialize and run InfraGuard
        app = InfraGuard(args.config)
        
        # Override log level if specified
        if args.log_level:
            import logging
            logging.getLogger().setLevel(getattr(logging, args.log_level))
        
        # Run application
        app.run()
        
    except ConfigurationError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        sys.exit(0)
    
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
