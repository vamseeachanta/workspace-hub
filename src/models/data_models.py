"""
ABOUTME: Data domain models for aceengineercode and digitalmodel projects
ABOUTME: Stores project-specific data with full audit and validation tracking
"""

from datetime import datetime
from sqlalchemy import Column, String, JSON, DateTime, Integer, Text, Boolean
from sqlalchemy.orm import relationship

from .base import Base, BaseModel, AuditMixin, MetadataMixin, StatusMixin


class DataModel(BaseModel, AuditMixin, MetadataMixin, StatusMixin):
    """Model for storing domain-specific project data."""

    __tablename__ = 'project_data'

    # Data identity
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    data_type = Column(String(100), nullable=False)  # e.g., "engineering", "financial", "operational"
    project_name = Column(String(255), nullable=False)  # e.g., "aceengineercode", "digitalmodel"

    # Data content
    data_payload = Column(JSON, nullable=False)  # Flexible JSON storage for any domain data
    schema_definition = Column(JSON, nullable=True)  # Optional schema for validation

    # Data lineage
    source_system = Column(String(255), nullable=True)  # Where data originated
    source_identifier = Column(String(255), nullable=True)  # External reference ID
    parent_data_id = Column(Integer, nullable=True)  # Reference to parent data for relationships

    # Data quality
    is_validated = Column(Boolean, default=False, nullable=False)
    validation_timestamp = Column(DateTime, nullable=True)
    data_quality_score = Column(String(50), nullable=True)  # e.g., "excellent", "good", "needs_review"
    quality_notes = Column(Text, nullable=True)

    # Data lifecycle
    source_file_path = Column(String(500), nullable=True)  # Original file location
    last_import_at = Column(DateTime, nullable=True)
    import_count = Column(Integer, default=0, nullable=False)

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'data_type': self.data_type,
            'project_name': self.project_name,
            'is_validated': self.is_validated,
            'data_quality_score': self.data_quality_score,
        })
        return base_dict

    def __repr__(self) -> str:
        """String representation."""
        return f"DataModel(name={self.name}, type={self.data_type}, project={self.project_name})"
