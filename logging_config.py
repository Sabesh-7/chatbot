import logging
import os
from datetime import datetime

def setup_logging():
    """Setup logging configuration for the application"""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Create log filename with timestamp
    log_filename = f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # File handler - logs to file
            logging.FileHandler(log_filename, encoding='utf-8'),
            # Console handler - logs to console
            logging.StreamHandler()
        ]
    )
    
    # Set specific log levels for different modules
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    # Create logger for the application
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    
    return logger

def get_logger(name):
    """Get a logger instance for a specific module"""
    return logging.getLogger(name) 