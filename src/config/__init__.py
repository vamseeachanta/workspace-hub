"""
ABOUTME: Configuration management module for unified YAML-based system configuration
ABOUTME: Provides schema validation, loading, and access for both aceengineercode and digitalmodel patterns
"""

from .config_loader import ConfigLoader
from .schema_validator import SchemaValidator
from .config_manager import ConfigManager

__all__ = [
    "ConfigLoader",
    "SchemaValidator",
    "ConfigManager",
]

__version__ = "1.0.0"
