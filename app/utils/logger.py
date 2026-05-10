"""
Logging utilities
Configure structured logging for the application
"""
import logging
import logging.config
import json
from pythonjsonlogger import jsonlogger


def setup_json_logging(app):
    """
    Setup JSON structured logging
    """
    if not app.debug:
        # Configure JSON logging
        logHandler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter()
        logHandler.setFormatter(formatter)
        app.logger.addHandler(logHandler)
        app.logger.setLevel(logging.INFO)


def get_logger(name):
    """
    Get a logger instance
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class RequestLogger:
    """Log HTTP requests"""
    
    @staticmethod
    def log_request(request):
        """Log incoming request"""
        logger = get_logger(__name__)
        logger.info(f'Request: {request.method} {request.path}')
    
    @staticmethod
    def log_response(response, duration=None):
        """Log outgoing response"""
        logger = get_logger(__name__)
        logger.info(
            f'Response: {response.status_code} - '
            f'{duration:.2f}s' if duration else ''
        )
