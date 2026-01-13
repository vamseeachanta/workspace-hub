"""
ABOUTME: Database connection management with pooling support
ABOUTME: Handles SQLite, SQL Server, and other database engines
"""

import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool, StaticPool

logger = logging.getLogger(__name__)


@dataclass
class ConnectionConfig:
    """Database connection configuration."""
    engine_type: str  # 'sqlite', 'mssql', 'postgresql', 'mysql'
    host: Optional[str] = None
    port: Optional[int] = None
    database: str = 'main'
    username: Optional[str] = None
    password: Optional[str] = None
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: float = 30
    pool_recycle: int = 3600
    echo: bool = False


class DatabaseConnection:
    """Manages individual database connections."""

    def __init__(self, config: ConnectionConfig):
        """
        Initialize database connection.

        Args:
            config: Connection configuration
        """
        self.config = config
        self.engine: Optional[Engine] = None
        self._create_connection()

    def _create_connection(self):
        """Create database engine based on configuration."""
        try:
            if self.config.engine_type == 'sqlite':
                connection_string = f"sqlite:///{self.config.database}"
                self.engine = create_engine(
                    connection_string,
                    echo=self.config.echo,
                    poolclass=StaticPool  # For testing
                )
            elif self.config.engine_type == 'mssql':
                connection_string = (
                    f"mssql+pyodbc://{self.config.username}:{self.config.password}"
                    f"@{self.config.host}:{self.config.port}/{self.config.database}"
                    f"?driver=ODBC+Driver+17+for+SQL+Server"
                )
                self.engine = create_engine(
                    connection_string,
                    echo=self.config.echo,
                    poolclass=QueuePool,
                    pool_size=self.config.pool_size,
                    max_overflow=self.config.max_overflow,
                    pool_timeout=self.config.pool_timeout,
                    pool_recycle=self.config.pool_recycle,
                )
            elif self.config.engine_type == 'postgresql':
                connection_string = (
                    f"postgresql://{self.config.username}:{self.config.password}"
                    f"@{self.config.host}:{self.config.port}/{self.config.database}"
                )
                self.engine = create_engine(
                    connection_string,
                    echo=self.config.echo,
                    poolclass=QueuePool,
                    pool_size=self.config.pool_size,
                    max_overflow=self.config.max_overflow,
                )
            else:
                raise ValueError(f"Unsupported engine type: {self.config.engine_type}")

            logger.info(
                f"Database connection created: {self.config.engine_type}"
                f"://{self.config.host}/{self.config.database}"
            )
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            raise

    def get_engine(self) -> Engine:
        """Get SQLAlchemy engine."""
        if self.engine is None:
            raise RuntimeError("Database engine not initialized")
        return self.engine

    def test_connection(self) -> bool:
        """Test database connectivity."""
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    def dispose(self):
        """Dispose of connection pool."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection disposed")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"DatabaseConnection({self.config.engine_type}://"
            f"{self.config.host}/{self.config.database})"
        )


class ConnectionPool:
    """Manages multiple database connections with pooling."""

    def __init__(self):
        """Initialize connection pool."""
        self.connections: Dict[str, DatabaseConnection] = {}
        self.default_connection: Optional[str] = None

    def add_connection(self, name: str, config: ConnectionConfig, default: bool = False):
        """
        Add a database connection to the pool.

        Args:
            name: Connection identifier
            config: Connection configuration
            default: Whether to use as default connection
        """
        connection = DatabaseConnection(config)
        self.connections[name] = connection

        if default or self.default_connection is None:
            self.default_connection = name

        logger.info(f"Added connection to pool: {name}")

    def get_connection(self, name: Optional[str] = None) -> DatabaseConnection:
        """
        Get a connection from the pool.

        Args:
            name: Connection name (uses default if not specified)

        Returns:
            DatabaseConnection instance
        """
        connection_name = name or self.default_connection

        if connection_name not in self.connections:
            raise ValueError(f"Connection not found: {connection_name}")

        return self.connections[connection_name]

    def get_engine(self, name: Optional[str] = None) -> Engine:
        """Get SQLAlchemy engine from connection."""
        connection = self.get_connection(name)
        return connection.get_engine()

    def test_all_connections(self) -> Dict[str, bool]:
        """Test all connections in the pool."""
        results = {}
        for name, connection in self.connections.items():
            results[name] = connection.test_connection()
        return results

    def dispose_all(self):
        """Dispose of all connections."""
        for connection in self.connections.values():
            connection.dispose()
        logger.info("All database connections disposed")

    def list_connections(self) -> list[str]:
        """Get list of available connection names."""
        return list(self.connections.keys())

    def __repr__(self) -> str:
        """String representation."""
        return f"ConnectionPool({len(self.connections)} connections)"
