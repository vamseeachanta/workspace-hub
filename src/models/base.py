"""
ABOUTME: Base SQLAlchemy models and mixins for all Phase 1 data models
ABOUTME: Provides common fields, relationships, and utilities
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import AbstractConcreteBase

Base = declarative_base()


class BaseModel(Base):
    """Abstract base model with common fields."""

    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(id={self.id})"


class AuditMixin:
    """Mixin for audit trail tracking."""

    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
    change_notes = Column(String(1000), nullable=True)


class MetadataMixin:
    """Mixin for metadata management."""

    metadata_json = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    version = Column(Integer, default=1, nullable=False)


class StatusMixin:
    """Mixin for status tracking."""

    status = Column(String(50), default='pending', nullable=False)
    status_message = Column(String(500), nullable=True)
    status_updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
