"""
ABOUTME: Database migration management for schema versioning
ABOUTME: Handles schema creation, upgrades, and rollbacks
"""

import logging
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
from sqlalchemy import MetaData, Table, Column, String, DateTime, create_engine
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


@dataclass
class Migration:
    """Represents a database migration."""
    version: str
    description: str
    created_at: datetime
    upgrade_func: Callable
    downgrade_func: Callable


class MigrationManager:
    """Manages database schema migrations."""

    def __init__(self, engine):
        """
        Initialize migration manager.

        Args:
            engine: SQLAlchemy engine
        """
        self.engine = engine
        self.migrations: Dict[str, Migration] = {}
        self.applied_migrations: List[str] = []
        self._create_migration_table()

    def _create_migration_table(self):
        """Create table to track applied migrations."""
        metadata = MetaData()

        # Define migrations table
        migrations_table = Table(
            'schema_migrations',
            metadata,
            Column('id', String(255), primary_key=True),
            Column('version', String(50), unique=True, nullable=False),
            Column('description', String(500)),
            Column('applied_at', DateTime, default=datetime.utcnow),
        )

        metadata.create_all(self.engine)
        logger.info("Migrations table created/verified")

    def register_migration(
        self,
        version: str,
        description: str,
        upgrade_func: Callable,
        downgrade_func: Callable
    ):
        """
        Register a migration.

        Args:
            version: Migration version (e.g., '001_initial_schema')
            description: Human-readable description
            upgrade_func: Function to execute migration
            downgrade_func: Function to rollback migration
        """
        migration = Migration(
            version=version,
            description=description,
            created_at=datetime.utcnow(),
            upgrade_func=upgrade_func,
            downgrade_func=downgrade_func
        )

        self.migrations[version] = migration
        logger.info(f"Registered migration: {version} - {description}")

    def get_applied_migrations(self) -> List[str]:
        """
        Get list of applied migrations.

        Returns:
            List of migration versions
        """
        with self.engine.connect() as conn:
            result = conn.execute(
                "SELECT version FROM schema_migrations ORDER BY applied_at"
            )
            self.applied_migrations = [row[0] for row in result]
        return self.applied_migrations

    def get_pending_migrations(self) -> List[str]:
        """
        Get list of pending migrations.

        Returns:
            List of migration versions not yet applied
        """
        applied = self.get_applied_migrations()
        pending = [v for v in sorted(self.migrations.keys()) if v not in applied]
        return pending

    def apply_migration(self, version: str, session: Session) -> bool:
        """
        Apply a single migration.

        Args:
            version: Migration version
            session: SQLAlchemy session

        Returns:
            True if successful
        """
        if version not in self.migrations:
            logger.error(f"Migration not found: {version}")
            return False

        if version in self.applied_migrations:
            logger.warning(f"Migration already applied: {version}")
            return True

        try:
            migration = self.migrations[version]
            migration.upgrade_func(session)

            # Record migration
            session.execute(
                f"INSERT INTO schema_migrations (version, description) "
                f"VALUES ('{version}', '{migration.description}')"
            )
            session.commit()

            logger.info(f"Applied migration: {version}")
            self.applied_migrations.append(version)
            return True
        except Exception as e:
            logger.error(f"Failed to apply migration {version}: {e}")
            session.rollback()
            return False

    def apply_all_pending(self, session: Session) -> int:
        """
        Apply all pending migrations.

        Args:
            session: SQLAlchemy session

        Returns:
            Number of migrations applied
        """
        pending = self.get_pending_migrations()
        count = 0

        for version in pending:
            if self.apply_migration(version, session):
                count += 1

        logger.info(f"Applied {count} migrations")
        return count

    def rollback_migration(self, version: str, session: Session) -> bool:
        """
        Rollback a migration.

        Args:
            version: Migration version
            session: SQLAlchemy session

        Returns:
            True if successful
        """
        if version not in self.migrations:
            logger.error(f"Migration not found: {version}")
            return False

        if version not in self.applied_migrations:
            logger.warning(f"Migration not applied: {version}")
            return True

        try:
            migration = self.migrations[version]
            migration.downgrade_func(session)

            # Remove from history
            session.execute(
                f"DELETE FROM schema_migrations WHERE version = '{version}'"
            )
            session.commit()

            logger.info(f"Rolled back migration: {version}")
            self.applied_migrations.remove(version)
            return True
        except Exception as e:
            logger.error(f"Failed to rollback migration {version}: {e}")
            session.rollback()
            return False

    def rollback_to_version(self, target_version: str, session: Session) -> int:
        """
        Rollback to a specific version.

        Args:
            target_version: Target migration version
            session: SQLAlchemy session

        Returns:
            Number of migrations rolled back
        """
        applied = self.get_applied_migrations()

        if target_version not in applied:
            logger.warning(f"Target version not in history: {target_version}")
            return 0

        # Rollback in reverse order
        to_rollback = applied[applied.index(target_version) + 1:]
        count = 0

        for version in reversed(to_rollback):
            if self.rollback_migration(version, session):
                count += 1

        return count

    def get_migration_status(self) -> Dict[str, str]:
        """
        Get status of all migrations.

        Returns:
            Dictionary of migration versions and their status
        """
        applied = self.get_applied_migrations()
        status = {}

        for version in sorted(self.migrations.keys()):
            status[version] = 'applied' if version in applied else 'pending'

        return status

    def generate_migration_report(self) -> str:
        """Generate migration status report."""
        status = self.get_migration_status()

        report = "Database Migration Status\n"
        report += "=" * 50 + "\n\n"

        for version, migration_status in status.items():
            migration = self.migrations[version]
            status_symbol = "✓" if migration_status == 'applied' else "○"
            report += f"{status_symbol} {version}: {migration.description}\n"
            report += f"   Status: {migration_status}\n\n"

        return report
