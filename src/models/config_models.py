"""
ABOUTME: Configuration models for unified YAML configuration management
ABOUTME: Stores configuration metadata, versions, and audit trails
"""

from datetime import datetime
from sqlalchemy import Column, String, JSON, DateTime, Integer, Text
from sqlalchemy.orm import relationship

from .base import Base, BaseModel, AuditMixin, MetadataMixin, StatusMixin


class ConfigModel(BaseModel, AuditMixin, MetadataMixin, StatusMixin):
    """Model for storing configuration instances."""

    __tablename__ = 'configurations'

    # Configuration identity
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    configuration_type = Column(String(100), nullable=False)  # e.g., "aceengineercode", "digitalmodel"

    # Configuration content
    config_data = Column(JSON, nullable=False)
    schema_version = Column(String(50), nullable=False)

    # Configuration management
    environment = Column(String(50), nullable=False)  # development, staging, production
    is_active_config = Column(String(50), default='draft', nullable=False)  # draft, approved, active, archived

    # Validation and verification
    validation_errors = Column(JSON, nullable=True)  # Array of validation error messages
    last_validated_at = Column(DateTime, nullable=True)
    validation_status = Column(String(50), default='unvalidated', nullable=False)  # unvalidated, valid, invalid

    # References
    parent_config_id = Column(Integer, nullable=True)  # Reference to parent config for inheritance

    def validate_config(self) -> bool:
        """Validate configuration against schema."""
        from ..config.schema_validator import SchemaValidator

        validator = SchemaValidator()
        valid, errors = validator.validate(self.config_data)

        self.validation_errors = errors if not valid else None
        self.validation_status = 'valid' if valid else 'invalid'
        self.last_validated_at = datetime.utcnow()

        return valid

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'configuration_type': self.configuration_type,
            'environment': self.environment,
            'validation_status': self.validation_status,
            'config_data': self.config_data,
        })
        return base_dict

    def __repr__(self) -> str:
        """String representation."""
        return f"ConfigModel(name={self.name}, env={self.environment}, valid={self.validation_status})"
