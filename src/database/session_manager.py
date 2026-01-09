"""
ABOUTME: SQLAlchemy session management for database operations
ABOUTME: Provides session factory, context management, and transaction handling
"""

import logging
from typing import Optional, Callable, Any
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages SQLAlchemy sessions for database operations."""

    def __init__(self, engine: Engine):
        """
        Initialize session manager.

        Args:
            engine: SQLAlchemy engine instance
        """
        self.engine = engine
        self.session_factory = sessionmaker(bind=engine)
        self.scoped_session = scoped_session(self.session_factory)

    def get_session(self) -> Session:
        """
        Get a new database session.

        Returns:
            SQLAlchemy Session instance
        """
        return self.session_factory()

    def get_scoped_session(self) -> Session:
        """
        Get a scoped session (thread-local).

        Returns:
            Scoped SQLAlchemy Session instance
        """
        return self.scoped_session()

    @contextmanager
    def session_context(self):
        """
        Context manager for database sessions.

        Yields:
            SQLAlchemy Session instance
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
            logger.debug("Session committed successfully")
        except Exception as e:
            session.rollback()
            logger.error(f"Session rolled back due to error: {e}")
            raise
        finally:
            session.close()

    def execute_in_transaction(self, operation: Callable, *args, **kwargs) -> Any:
        """
        Execute operation within a transaction.

        Args:
            operation: Callable to execute
            args: Positional arguments for operation
            kwargs: Keyword arguments for operation

        Returns:
            Result of operation
        """
        with self.session_context() as session:
            return operation(session, *args, **kwargs)

    def execute_batch(self, operations: list[tuple[Callable, tuple, dict]]) -> list[Any]:
        """
        Execute multiple operations in a single transaction.

        Args:
            operations: List of (callable, args, kwargs) tuples

        Returns:
            List of operation results
        """
        results = []
        with self.session_context() as session:
            for operation, args, kwargs in operations:
                result = operation(session, *args, **kwargs)
                results.append(result)
        return results

    def clear_scoped_session(self):
        """Clear scoped session."""
        self.scoped_session.remove()
        logger.debug("Scoped session cleared")

    def close_all(self):
        """Close all sessions."""
        self.scoped_session.remove()
        logger.info("All sessions closed")


class TransactionManager:
    """Manages explicit transaction control."""

    def __init__(self, session: Session):
        """
        Initialize transaction manager.

        Args:
            session: SQLAlchemy session
        """
        self.session = session
        self.transaction = None

    def begin(self):
        """Begin a transaction."""
        self.transaction = self.session.begin()
        logger.debug("Transaction begun")

    def commit(self):
        """Commit the transaction."""
        if self.transaction:
            self.transaction.commit()
            logger.debug("Transaction committed")

    def rollback(self):
        """Rollback the transaction."""
        if self.transaction:
            self.transaction.rollback()
            logger.debug("Transaction rolled back")

    def savepoint(self, name: str):
        """Create a savepoint."""
        self.session.execute(f"SAVEPOINT {name}")
        logger.debug(f"Savepoint created: {name}")

    def rollback_to_savepoint(self, name: str):
        """Rollback to a savepoint."""
        self.session.execute(f"ROLLBACK TO {name}")
        logger.debug(f"Rolled back to savepoint: {name}")
