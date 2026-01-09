"""
ABOUTME: Unified SQLAlchemy ORM models for consolidated aceengineercode and digitalmodel data
ABOUTME: Provides base classes and concrete model definitions for Phase 1
"""

from .base import Base, BaseModel

# Concrete model implementations (Task 1.4.1-1.4.3) to be created in Phase 1.1
# from .config_models import ConfigModel
# from .solver_models import SolverModel, SolverResult
# from .data_models import DataModel

__all__ = [
    "Base",
    "BaseModel",
    # "ConfigModel",
    # "SolverModel",
    # "SolverResult",
    # "DataModel",
]

__version__ = "1.0.0"
