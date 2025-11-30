"""
Validators Module

Validation utilities for configuration, data, and user input.
"""

from typing import Dict, Any, List
import re


class ValidationError(Exception):
    """Exception for validation errors."""
    pass


class ConfigValidator:
    """Validates configuration dictionaries."""

    REQUIRED_SECTIONS = ['stt', 'microphone', 'nlp', 'inventory', 'database', 'response', 'logging']

    def validate(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration dictionary.

        Args:
            config: Configuration dictionary

        Returns:
            True if valid

        Raises:
            ValidationError: If configuration is invalid
        """
        # Check required sections
        for section in self.REQUIRED_SECTIONS:
            if section not in config:
                raise ValidationError(f"Missing required config section: {section}")

        # Validate STT config
        self._validate_stt(config['stt'])

        # Validate database config
        self._validate_database(config['database'])

        # Validate logging config
        self._validate_logging(config['logging'])

        return True

    def _validate_stt(self, stt_config: Dict[str, Any]):
        """Validate STT configuration."""
        provider = stt_config.get('provider', '').lower()
        valid_providers = ['google', 'sphinx', 'whisper']

        if provider not in valid_providers:
            raise ValidationError(
                f"Invalid STT provider: {provider}. "
                f"Must be one of: {', '.join(valid_providers)}"
            )

    def _validate_database(self, db_config: Dict[str, Any]):
        """Validate database configuration."""
        if 'path' not in db_config:
            raise ValidationError("Database path is required")

    def _validate_logging(self, log_config: Dict[str, Any]):
        """Validate logging configuration."""
        level = log_config.get('level', '').upper()
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

        if level not in valid_levels:
            raise ValidationError(
                f"Invalid log level: {level}. "
                f"Must be one of: {', '.join(valid_levels)}"
            )


class DataValidator:
    """Validates inventory data."""

    @staticmethod
    def validate_item_name(name: str) -> bool:
        """
        Validate item name.

        Args:
            name: Item name

        Returns:
            True if valid

        Raises:
            ValidationError: If invalid
        """
        if not name or not name.strip():
            raise ValidationError("Item name cannot be empty")

        if len(name) > 100:
            raise ValidationError("Item name too long (max 100 characters)")

        # Check for invalid characters
        if re.search(r'[<>:"/\\|?*]', name):
            raise ValidationError("Item name contains invalid characters")

        return True

    @staticmethod
    def validate_quantity(quantity: int) -> bool:
        """
        Validate quantity.

        Args:
            quantity: Quantity value

        Returns:
            True if valid

        Raises:
            ValidationError: If invalid
        """
        if not isinstance(quantity, int):
            raise ValidationError("Quantity must be an integer")

        if quantity < 0:
            raise ValidationError("Quantity cannot be negative")

        if quantity > 1000000:
            raise ValidationError("Quantity too large (max 1,000,000)")

        return True

    @staticmethod
    def validate_price(price: float) -> bool:
        """
        Validate price.

        Args:
            price: Price value

        Returns:
            True if valid

        Raises:
            ValidationError: If invalid
        """
        if not isinstance(price, (int, float)):
            raise ValidationError("Price must be a number")

        if price < 0:
            raise ValidationError("Price cannot be negative")

        if price > 1000000:
            raise ValidationError("Price too large (max 1,000,000)")

        return True

    @staticmethod
    def validate_category(category: str) -> bool:
        """
        Validate category.

        Args:
            category: Category name

        Returns:
            True if valid

        Raises:
            ValidationError: If invalid
        """
        if not category or not category.strip():
            raise ValidationError("Category cannot be empty")

        if len(category) > 50:
            raise ValidationError("Category name too long (max 50 characters)")

        return True


class InputValidator:
    """Validates user input."""

    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitize user input text.

        Args:
            text: Input text

        Returns:
            Sanitized text
        """
        # Remove leading/trailing whitespace
        text = text.strip()

        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)

        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

        return text

    @staticmethod
    def validate_command(command: str) -> bool:
        """
        Validate voice command.

        Args:
            command: Command text

        Returns:
            True if valid

        Raises:
            ValidationError: If invalid
        """
        if not command or not command.strip():
            raise ValidationError("Command cannot be empty")

        if len(command) > 500:
            raise ValidationError("Command too long (max 500 characters)")

        return True
