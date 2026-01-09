"""
ABOUTME: JSON schema definitions and validation for unified configuration system
ABOUTME: Ensures configuration consistency across all Phase 1 tasks
"""

from typing import Dict, Any, Optional
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class SchemaValidator:
    """Configuration schema validation and definition management."""

    # Base configuration schema
    BASE_SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Unified Configuration Schema",
        "description": "Schema for unified YAML configuration supporting aceengineercode and digitalmodel patterns",
        "type": "object",
        "properties": {
            "metadata": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "version": {"type": "string"},
                    "created": {"type": "string", "format": "date-time"},
                    "author": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["name", "version"],
            },
            "configuration": {
                "type": "object",
                "properties": {
                    "aceengineercode": {
                        "type": "object",
                        "description": "aceengineercode-specific configuration",
                    },
                    "digitalmodel": {
                        "type": "object",
                        "description": "digitalmodel-specific configuration",
                    },
                    "shared": {
                        "type": "object",
                        "description": "Shared configuration for both systems",
                    },
                },
            },
            "database": {
                "type": "object",
                "properties": {
                    "engine": {"type": "string", "enum": ["sqlite", "postgresql", "mssql"]},
                    "host": {"type": "string"},
                    "port": {"type": "integer"},
                    "database": {"type": "string"},
                    "pool_size": {"type": "integer", "minimum": 1},
                    "max_overflow": {"type": "integer", "minimum": 0},
                },
            },
            "logging": {
                "type": "object",
                "properties": {
                    "level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
                    "format": {"type": "string"},
                    "handlers": {
                        "type": "object",
                        "properties": {
                            "console": {"type": "boolean"},
                            "file": {"type": "boolean"},
                            "file_path": {"type": "string"},
                        },
                    },
                },
            },
            "performance": {
                "type": "object",
                "properties": {
                    "config_load_timeout_ms": {"type": "integer", "minimum": 100, "maximum": 1000},
                    "solver_timeout_ms": {"type": "integer", "minimum": 100},
                    "query_timeout_ms": {"type": "integer", "minimum": 100},
                    "connection_timeout_ms": {"type": "integer", "minimum": 50},
                },
            },
        },
    }

    def __init__(self):
        """Initialize schema validator."""
        self.schema = self.BASE_SCHEMA.copy()

    def validate(self, config: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate configuration against schema.

        Args:
            config: Configuration dictionary to validate

        Returns:
            Tuple of (valid: bool, errors: list[str])
        """
        try:
            import jsonschema

            jsonschema.validate(instance=config, schema=self.schema)
            logger.info("Configuration validation successful")
            return True, []

        except jsonschema.ValidationError as e:
            error_msg = f"Schema validation error at {e.json_path}: {e.message}"
            logger.error(error_msg)
            return False, [error_msg]

        except ImportError:
            logger.warning("jsonschema not installed, skipping validation")
            return True, []

    def get_schema(self) -> Dict[str, Any]:
        """Get current schema definition."""
        return self.schema.copy()

    def save_schema(self, output_file: Path):
        """Save schema to JSON file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(self.schema, f, indent=2)
            logger.info(f"Schema saved to: {output_file}")
        except Exception as e:
            logger.error(f"Failed to save schema: {e}")
            raise

    def extend_schema(self, schema_extension: Dict[str, Any]):
        """
        Extend schema with additional properties.

        Args:
            schema_extension: Dictionary of schema properties to add
        """
        if "properties" not in self.schema:
            self.schema["properties"] = {}

        self.schema["properties"].update(schema_extension)
        logger.info(f"Schema extended with {len(schema_extension)} properties")

    @staticmethod
    def create_backend_schema() -> Dict[str, Any]:
        """Create schema for backend/infrastructure configuration."""
        return {
            "type": "object",
            "properties": {
                "backend": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ["local", "docker", "kubernetes"]},
                        "workers": {"type": "integer", "minimum": 1},
                        "timeout": {"type": "integer", "minimum": 0},
                    },
                },
            },
        }

    @staticmethod
    def create_solver_schema() -> Dict[str, Any]:
        """Create schema for mathematical solver configuration."""
        return {
            "type": "object",
            "properties": {
                "solvers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "module": {"type": "string"},
                            "enabled": {"type": "boolean"},
                            "timeout_ms": {"type": "integer", "minimum": 100},
                            "accuracy_tolerance": {"type": "number", "minimum": 0, "maximum": 1},
                        },
                        "required": ["name", "module"],
                    },
                },
            },
        }
