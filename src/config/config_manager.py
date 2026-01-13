"""
ABOUTME: Main configuration manager orchestrating loader and validator
ABOUTME: Provides unified interface for configuration access across Phase 1
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from .config_loader import ConfigLoader, ConfigValidator
from .schema_validator import SchemaValidator

logger = logging.getLogger(__name__)


class ConfigManager:
    """Unified configuration management system."""

    def __init__(self, config_file: Optional[Path | str] = None, schema_file: Optional[Path | str] = None):
        """
        Initialize configuration manager.

        Args:
            config_file: Path to YAML configuration file
            schema_file: Path to JSON schema file for validation
        """
        self.config_loader = ConfigLoader()
        self.schema_validator = SchemaValidator()
        self.config: Dict[str, Any] = {}

        if schema_file:
            self.config_validator = ConfigValidator(Path(schema_file))
        else:
            self.config_validator = None

        if config_file:
            self.load_config(config_file)

    def load_config(self, config_file: Path | str) -> bool:
        """
        Load configuration from file.

        Args:
            config_file: Path to YAML configuration file

        Returns:
            True if load successful, False otherwise
        """
        try:
            self.config = self.config_loader.load(config_file)

            # Validate if validator available
            if self.config_validator:
                valid, errors = self.config_validator.validate(self.config)
                if not valid:
                    logger.warning(f"Configuration validation warnings: {errors}")

            logger.info(f"Configuration loaded successfully from: {config_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated key.

        Args:
            key: Configuration key (supports nested keys with dots, e.g., "database.host")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value if value is not None else default

    def set(self, key: str, value: Any):
        """
        Set configuration value by dot-separated key.

        Args:
            key: Configuration key (supports nested keys)
            value: Value to set
        """
        keys = key.split('.')
        current = self.config

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value
        logger.debug(f"Configuration updated: {key}")

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section.

        Args:
            section: Section name

        Returns:
            Section dictionary or empty dict if not found
        """
        return self.config.get(section, {})

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate current configuration.

        Returns:
            Tuple of (valid: bool, errors: list[str])
        """
        if not self.config_validator:
            logger.warning("No validator available")
            return True, []

        return self.config_validator.validate(self.config)

    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self.config.copy()

    def reload(self, config_file: Path | str) -> bool:
        """
        Reload configuration from file.

        Args:
            config_file: Path to YAML configuration file

        Returns:
            True if reload successful
        """
        self.config_loader.clear_cache()
        return self.load_config(config_file)

    @property
    def is_valid(self) -> bool:
        """Check if current configuration is valid."""
        if not self.config_validator:
            return True

        valid, _ = self.validate()
        return valid

    @property
    def size(self) -> int:
        """Return number of configuration keys."""
        return len(self.config)

    def __repr__(self) -> str:
        """String representation of configuration manager."""
        return f"ConfigManager(size={self.size}, valid={self.is_valid})"
