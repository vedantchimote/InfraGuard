"""
Health check HTTP server for InfraGuard.

Provides a simple HTTP endpoint for health checks and status monitoring.
"""

import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Callable
import json


logger = logging.getLogger(__name__)


class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP request handler for health checks."""
    
    # Class variable to store status callback
    status_callback: Optional[Callable] = None
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/health':
            self.handle_health()
        elif self.path == '/':
            self.handle_root()
        else:
            self.send_error(404, "Not Found")
    
    def handle_health(self):
        """Handle /health endpoint."""
        try:
            # Get status from callback if available
            if self.status_callback:
                status = self.status_callback()
            else:
                status = {'status': 'unknown'}
            
            # Add basic health info
            response = {
                'status': 'healthy' if status.get('running', False) else 'stopped',
                'service': 'InfraGuard AIOps',
                **status
            }
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            self.send_error(500, f"Internal Server Error: {e}")
    
    def handle_root(self):
        """Handle / endpoint."""
        response = {
            'service': 'InfraGuard AIOps',
            'version': '0.1.0',
            'endpoints': {
                '/health': 'Health check and status'
            }
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def log_message(self, format, *args):
        """Override to use Python logging instead of stderr."""
        logger.debug(f"{self.address_string()} - {format % args}")


class HealthServer:
    """
    HTTP server for health checks.
    
    Runs in a separate thread to provide health status without
    blocking the main application.
    
    Attributes:
        port: HTTP port to listen on
        status_callback: Function to get application status
        server: HTTPServer instance
        thread: Server thread
    
    Example:
        >>> def get_status():
        ...     return {'running': True, 'last_collection': '2024-01-01T00:00:00'}
        >>> health_server = HealthServer(8000, get_status)
        >>> health_server.start()
    """
    
    def __init__(self, port: int, status_callback: Callable):
        """
        Initialize health server.
        
        Args:
            port: HTTP port to listen on
            status_callback: Function that returns status dictionary
        """
        self.port = port
        self.status_callback = status_callback
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None
        
        # Set status callback on handler class
        HealthCheckHandler.status_callback = status_callback
        
        logger.info(f"Health server initialized on port {port}")
    
    def start(self):
        """Start health server in background thread."""
        try:
            self.server = HTTPServer(('0.0.0.0', self.port), HealthCheckHandler)
            
            self.thread = threading.Thread(
                target=self.server.serve_forever,
                daemon=True,
                name='HealthServer'
            )
            self.thread.start()
            
            logger.info(f"Health server started on http://0.0.0.0:{self.port}")
            logger.info(f"Health endpoint: http://0.0.0.0:{self.port}/health")
            
        except Exception as e:
            logger.error(f"Failed to start health server: {e}")
            raise
    
    def stop(self):
        """Stop health server."""
        if self.server:
            logger.info("Stopping health server...")
            self.server.shutdown()
            self.server.server_close()
            
            if self.thread:
                self.thread.join(timeout=5)
            
            logger.info("Health server stopped")
