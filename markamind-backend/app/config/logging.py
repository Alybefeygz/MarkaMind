import logging
import sys
from .settings import settings


def setup_logging():
    """Setup logging configuration based on environment settings."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper())
    
    # Define log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure handlers based on environment
    handlers = []
    if settings.ENVIRONMENT == "production":
        # Production: log to file
        handlers.append(logging.FileHandler("backend.log"))
    else:
        # Development: log to stdout
        handlers.append(logging.StreamHandler(sys.stdout))
    
    # Setup basic configuration
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers,
        force=True  # Override any existing configuration
    )
    
    # Suppress third-party library logs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured for {settings.ENVIRONMENT} environment at {settings.LOG_LEVEL} level")
    
    return logger