"""
ABOUTME: Mathematical solver registry providing unified access to 25+ specialized solvers
ABOUTME: Implements registry pattern for dynamic solver discovery, loading, and execution
"""

from .registry import SolverRegistry
from .base import BaseSolver

__all__ = [
    "SolverRegistry",
    "BaseSolver",
]

__version__ = "1.0.0"

# Global solver registry instance
_registry = None


def get_registry() -> SolverRegistry:
    """Get global solver registry instance."""
    global _registry
    if _registry is None:
        _registry = SolverRegistry()
    return _registry
