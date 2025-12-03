"""
AppleTrader Pro - Logging System
Professional logging with file and console output
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'
    }

    def format(self, record):
        # Add color to levelname
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"

        # Format the message
        formatted = super().format(record)

        return formatted


class AppLogger:
    """Application logger with file and console output"""

    def __init__(self, name: str = "AppleTrader", log_dir: Optional[Path] = None):
        self.name = name
        self.log_dir = log_dir or Path(__file__).parent.parent.parent / "shared" / "data" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Remove existing handlers
        self.logger.handlers = []

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler (daily log files)
        log_file = self.log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)

    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)

    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)

    def exception(self, message: str):
        """Log exception with traceback"""
        self.logger.exception(message)

    def trade(self, message: str):
        """Log trading-related message (INFO level with prefix)"""
        self.logger.info(f"[TRADE] {message}")

    def ml(self, message: str):
        """Log ML-related message (INFO level with prefix)"""
        self.logger.info(f"[ML] {message}")

    def connection(self, message: str):
        """Log connection-related message (INFO level with prefix)"""
        self.logger.info(f"[CONNECTION] {message}")


# Global logger instance
logger = AppLogger("AppleTrader")


# Convenience functions
def debug(msg: str):
    logger.debug(msg)


def info(msg: str):
    logger.info(msg)


def warning(msg: str):
    logger.warning(msg)


def error(msg: str):
    logger.error(msg)


def critical(msg: str):
    logger.critical(msg)


def exception(msg: str):
    logger.exception(msg)


def trade(msg: str):
    logger.trade(msg)


def ml(msg: str):
    logger.ml(msg)


def connection(msg: str):
    logger.connection(msg)
