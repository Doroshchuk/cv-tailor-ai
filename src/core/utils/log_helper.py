import logging
from typing import Optional
from enum import Enum


class LogLevelEnum(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogHelper:
    DEFAULT_FORMAT_STRING = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def __init__(self, name: str, log_level: LogLevelEnum = LogLevelEnum.INFO):
        self.logger = self._setup_logger(name, log_level)
    
    @staticmethod
    def _setup_logger(name: str, log_level: LogLevelEnum) -> logging.Logger:
        """Set up and configure a logger with the given name"""
        logger = logging.getLogger(name)
        
        # Only add handlers if they don't already exist
        if not logger.handlers:
            logger.setLevel(log_level.name)
            
            # Create console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level.name)
            
            # Create formatter
            formatter = logging.Formatter(
                LogHelper.DEFAULT_FORMAT_STRING
            )
            console_handler.setFormatter(formatter)
            
            # Add handler to logger
            logger.addHandler(console_handler)
        
        return logger
    
    def info(self, message: str) -> None:
        """Log info message"""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message"""
        self.logger.error(message)
    
    def debug(self, message: str) -> None:
        """Log debug message"""
        self.logger.debug(message)
    
    def critical(self, message: str) -> None:
        """Log critical message"""
        self.logger.critical(message)

    @classmethod
    def configure_logging(cls, level: str = "INFO", 
                         log_file: Optional[str] = None,
                         format_string: str = DEFAULT_FORMAT_STRING) -> None:
        """Configure logging with custom settings for all loggers"""
        # Set root logger level
        logging.getLogger().setLevel(getattr(logging, level.upper()))
        
        # Configure all existing loggers
        for logger_name in logging.root.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            logger.setLevel(getattr(logging, level.upper()))
            
            # Clear existing handlers
            logger.handlers.clear()
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, level.upper()))
            
            # File handler (if specified)
            if log_file:
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(getattr(logging, level.upper()))
                logger.addHandler(file_handler)
            
            # Formatter
            formatter = logging.Formatter(
                format_string
            )
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)