import logging
from datetime import datetime

def get_logger(module_name: str):
    logger = logging.getLogger(module_name)
    handler = logging.FileHandler(f'logs/{module_name}.log')
    
    # Format: timestamp|service|endpoint|status_code|latency_ms|message
    formatter = logging.Formatter(
        '%(asctime)s|%(service_name)s|%(endpoint)s|%(status_code)s|%(latency_ms)s|%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger

def log_request(logger, service_name: str, endpoint: str, status_code: int, latency_ms: float, message: str):
    """Helper function to log requests with consistent format"""
    logger.info(
        message,
        extra={
            "service_name": service_name,
            "endpoint": endpoint,
            "status_code": status_code,
            "latency_ms": latency_ms
        }
    )
