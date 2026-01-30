import logging
import sys
from pythonjsonlogger import jsonlogger
import os
from datetime import datetime

def setup_logging():
    """Setup structured logging for the application"""

    # Get log level from environment, default to INFO
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

    # Create a custom JSON formatter
    json_formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(filename)s %(lineno)d %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S'
    )

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Create handler for stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(json_formatter)
    root_logger.addHandler(handler)

    # Also setup specific loggers for different components
    logging.getLogger('uvicorn').setLevel(getattr(logging, log_level))
    logging.getLogger('uvicorn.access').setLevel(getattr(logging, log_level))
    logging.getLogger('uvicorn.error').setLevel(getattr(logging, log_level))
    logging.getLogger('fastapi').setLevel(getattr(logging, log_level))
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)  # Reduce SQLAlchemy noise
    logging.getLogger('confluent_kafka').setLevel(getattr(logging, log_level))

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(name)

# Initialize logging when module is imported
setup_logging()