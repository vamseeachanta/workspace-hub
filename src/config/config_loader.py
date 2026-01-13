"""
ABOUTME: YAML configuration file loading and parsing with performance optimization
ABOUTME: Supports both aceengineercode and digitalmodel configuration patterns
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Load and parse unified YAML configuration files."""

    def __init__(self, cache_enabled: bool = True, cache_ttl: int = 300):
        """
        Initialize configuration loader.

        Args:
            cache_enabled: Enable config file caching
            cache_ttl: Cache time-to-live in seconds (default: 300s = 5 min)
        """
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, tuple[dict, float]] = {}

    def load(self, config_file: Path | str) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Args:
            config_file: Path to YAML configuration file

        Returns:
            Parsed configuration dictionary

        Raises:
            FileNotFoundError: Configuration file not found
            yaml.YAMLError: Invalid YAML syntax
            TypeError: Unsupported file type
        """
        config_path = Path(config_file)

        # Validate file exists
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        # Check cache
        if self.cache_enabled and str(config_path) in self._cache:
            cached_config, cached_time = self._cache[str(config_path)]
            if datetime.now().timestamp() - cached_time < self.cache_ttl:
                logger.debug(f"Configuration loaded from cache: {config_path}")
                return cached_config

        # Load from file
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            if config is None:
                config = {}

            # Cache result
            if self.cache_enabled:
                self._cache[str(config_path)] = (config, datetime.now().timestamp())

            logger.info(f"Configuration loaded: {config_path}")
            return config

        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in {config_path}: {e}")
            raise

    def load_multiple(self, config_files: list[Path | str]) -> Dict[str, Any]:
        """
        Load and merge multiple configuration files.

        Configuration files are merged in order, with later files overriding earlier ones.

        Args:
            config_files: List of configuration file paths

        Returns:
            Merged configuration dictionary
        """
        merged_config = {}

        for config_file in config_files:
            config = self.load(config_file)
            merged_config.update(config)
            logger.debug(f"Merged configuration from: {config_file}")

        return merged_config

    def clear_cache(self):
        """Clear configuration cache."""
        self._cache.clear()
        logger.debug("Configuration cache cleared")


class ConfigValidator:
    """Validate configuration against schema."""

    def __init__(self, schema_file: Optional[Path] = None):
        """
        Initialize configuration validator.

        Args:
            schema_file: Optional JSON schema file for validation
        """
        self.schema_file = schema_file
        self.schema = None

        if schema_file:
            self._load_schema(schema_file)

    def _load_schema(self, schema_file: Path):
        """Load JSON schema from file."""
        import json

        try:
            with open(schema_file, 'r') as f:
                self.schema = json.load(f)
            logger.info(f"Schema loaded: {schema_file}")
        except Exception as e:
            logger.error(f"Failed to load schema: {e}")
            raise

    def validate(self, config: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate configuration against schema.

        Args:
            config: Configuration dictionary to validate

        Returns:
            Tuple of (valid: bool, errors: list[str])
        """
        if not self.schema:
            logger.warning("No schema loaded, skipping validation")
            return True, []

        try:
            import jsonschema

            jsonschema.validate(instance=config, schema=self.schema)
            logger.info("Configuration validation passed")
            return True, []

        except jsonschema.ValidationError as e:
            error_msg = f"Configuration validation failed: {e.message}"
            logger.error(error_msg)
            return False, [error_msg]
        except Exception as e:
            error_msg = f"Configuration validation error: {e}"
            logger.error(error_msg)
            return False, [error_msg]
