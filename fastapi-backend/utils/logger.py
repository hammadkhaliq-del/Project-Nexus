"""
Logging Configuration for NEXUS System
Provides consistent logging across all modules
"""
import logging
import sys
from typing import Optional
from datetime import datetime

from utils.config import settings


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for terminal output"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        color = self. COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Add color to level name
        record.levelname = f"{color}{record.levelname}{reset}"
        
        return super().format(record)


def setup_logger(
    name:  str,
    level: Optional[str] = None
) -> logging.Logger:
    """
    Setup and return a logger instance
    
    Args:
        name: Logger name (usually __name__)
        level: Log level (defaults to settings.LOG_LEVEL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Set level
    log_level = getattr(logging, level or settings.LOG_LEVEL, logging.INFO)
    logger.setLevel(log_level)
    
    # Console handler with colors
    console_handler = logging. StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Format
    formatter = ColoredFormatter(
        fmt='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


# Create default logger for the module
default_logger = setup_logger("nexus")


def log_event(event_type: str, message: str, data: dict = None):
    """Log a simulation event"""
    default_logger. info(f"[{event_type. upper()}] {message}")
    if data and settings.DEBUG:
        default_logger.debug(f"  Data: {data}")


def log_ai_decision(engine: str, decision: str, reasoning: str):
    """Log an AI engine decision"""
    default_logger. info(f"[AI:{engine. upper()}] {decision}")
    if settings.XAI_VERBOSE:
        default_logger.debug(f"  Reasoning: {reasoning}")