"""
Structured Logging Utility
Provides consistent logging across the application with request tracing
"""

import structlog
import logging
import sys
from typing import Any, Dict
from datetime import datetime
import uuid


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure structured logging with JSON format for production
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a logger instance with the given name
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured logger instance
    """
    return structlog.get_logger(name)


class RequestContextLogger:
    """
    Context manager for request-scoped logging
    Automatically adds request_id and other context to all logs
    """
    
    def __init__(self, user_id: str = None, query: str = None):
        self.request_id = str(uuid.uuid4())
        self.user_id = user_id
        self.query = query
        self.start_time = datetime.utcnow()
        self.logger = get_logger("request")
    
    def __enter__(self):
        """Start request context"""
        context = {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "timestamp": self.start_time.isoformat(),
        }
        if self.query:
            context["query"] = self.query[:100]  # Truncate long queries
        
        self.logger.info("request_started", **context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End request context"""
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()
        
        if exc_type is not None:
            self.logger.error(
                "request_failed",
                request_id=self.request_id,
                duration_seconds=duration,
                error_type=exc_type.__name__,
                error_message=str(exc_val)
            )
        else:
            self.logger.info(
                "request_completed",
                request_id=self.request_id,
                duration_seconds=duration
            )
    
    def log(self, level: str, message: str, **kwargs):
        """
        Log a message with request context
        
        Args:
            level: Log level (info, warning, error, debug)
            message: Log message
            **kwargs: Additional context
        """
        log_method = getattr(self.logger, level.lower())
        log_method(message, request_id=self.request_id, **kwargs)
