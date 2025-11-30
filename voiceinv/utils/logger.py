"""
Logging Module

Comprehensive logging system with multiple output formats and rotation.

Features:
- File and console logging
- Rotating file handlers
- Colored console output
- JSON log format option
- Separate log channels
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
import colorlog


# Global logger registry
_loggers = {}


def setup_logger(
    level: str = "INFO",
    log_to_file: bool = True,
    log_file_path: str = "logs/voice_inventory.log",
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    log_format: str = "detailed"
):
    """
    Setup the logging system.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Enable file logging
        log_file_path: Path to log file
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep
        log_format: Format type (simple, detailed, json)
    """
    # Create logs directory
    log_file = Path(log_file_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler with colors
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))

    if log_format == "simple":
        console_format = "%(log_color)s%(levelname)-8s%(reset)s %(message)s"
    elif log_format == "json":
        console_format = "%(log_color)s%(levelname)-8s%(reset)s %(message)s"
    else:  # detailed
        console_format = (
            "%(log_color)s%(levelname)-8s%(reset)s "
            "%(cyan)s%(asctime)s%(reset)s "
            "%(blue)s%(name)s%(reset)s "
            "%(message)s"
        )

    console_formatter = colorlog.ColoredFormatter(
        console_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler with rotation
    if log_to_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)  # Log everything to file

        if log_format == "json":
            file_format = '{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        else:
            file_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        file_formatter = logging.Formatter(
            file_format,
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    if name not in _loggers:
        _loggers[name] = logging.getLogger(name)

    return _loggers[name]


class VoiceCommandLogger:
    """Special logger for voice commands."""

    def __init__(self, log_file: str = "logs/voice_commands.log"):
        """
        Initialize voice command logger.

        Args:
            log_file: Path to voice command log file
        """
        self.logger = logging.getLogger("voice_commands")
        self.logger.setLevel(logging.INFO)

        # Create file handler
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3
        )

        formatter = logging.Formatter(
            "%(asctime)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def log_command(self, text: str, intent: str = None, success: bool = True):
        """
        Log a voice command.

        Args:
            text: Command text
            intent: Detected intent
            success: Whether command was successful
        """
        status = "SUCCESS" if success else "FAILED"
        intent_str = f" [{intent}]" if intent else ""

        self.logger.info(f"{status}{intent_str} - {text}")


class NLPLogger:
    """Special logger for NLP parsing."""

    def __init__(self, log_file: str = "logs/nlp_parsing.log"):
        """
        Initialize NLP logger.

        Args:
            log_file: Path to NLP log file
        """
        self.logger = logging.getLogger("nlp_parsing")
        self.logger.setLevel(logging.DEBUG)

        # Create file handler
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=3
        )

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def log_parse(self, text: str, intent: str, entities: dict, confidence: float):
        """
        Log an NLP parse result.

        Args:
            text: Input text
            intent: Detected intent
            entities: Extracted entities
            confidence: Confidence score
        """
        self.logger.debug(
            f"Text: '{text}' | Intent: {intent} | "
            f"Entities: {entities} | Confidence: {confidence:.2f}"
        )
