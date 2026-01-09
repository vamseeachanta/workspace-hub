"""
ABOUTME: Database integration layer for all Phase 1 modules
ABOUTME: Provides connection pooling, session management, and ORM integration
"""

from .connection import DatabaseConnection, ConnectionPool
from .session_manager import SessionManager
from .migrations import MigrationManager

__all__ = [
    "DatabaseConnection",
    "ConnectionPool",
    "SessionManager",
    "MigrationManager",
]

__version__ = "1.0.0"
