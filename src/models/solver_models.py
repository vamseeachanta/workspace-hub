"""
ABOUTME: Solver models for mathematical solver execution and result tracking
ABOUTME: Manages solver registrations, inputs, outputs, and performance metrics
"""

from datetime import datetime
from sqlalchemy import Column, String, JSON, DateTime, Float, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, BaseModel, AuditMixin, MetadataMixin, StatusMixin


class SolverModel(BaseModel, AuditMixin, MetadataMixin, StatusMixin):
    """Model for registering and tracking mathematical solvers."""

    __tablename__ = 'solvers'

    # Solver identity
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    module_path = Column(String(500), nullable=False)  # e.g., "src.solvers.linear_solver"
    class_name = Column(String(255), nullable=False)  # e.g., "LinearSolver"

    # Solver configuration
    solver_type = Column(String(100), nullable=False)  # e.g., "linear", "nonlinear", "optimization"
    version = Column(String(50), nullable=False)
    dependencies = Column(JSON, nullable=True)  # Required packages and versions
    configuration = Column(JSON, nullable=True)  # Solver-specific configuration

    # Performance characteristics
    average_execution_time_ms = Column(Float, nullable=True)
    max_execution_time_ms = Column(Float, nullable=True)
    min_execution_time_ms = Column(Float, nullable=True)
    total_executions = Column(Integer, default=0, nullable=False)

    # Accuracy and reliability
    accuracy_tolerance = Column(Float, nullable=True)
    success_rate = Column(Float, nullable=True)  # Percentage (0-100)
    last_error_message = Column(Text, nullable=True)

    # Operational status
    is_enabled = Column(String(50), default='enabled', nullable=False)  # enabled, disabled, deprecated
    is_lazy_loaded = Column(String(50), default='true', nullable=False)  # true, false

    # Relationships
    solver_results = relationship('SolverResult', back_populates='solver', foreign_keys='SolverResult.solver_id')

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'solver_type': self.solver_type,
            'version': self.version,
            'module_path': self.module_path,
            'is_enabled': self.is_enabled,
            'average_execution_time_ms': self.average_execution_time_ms,
            'success_rate': self.success_rate,
        })
        return base_dict

    def __repr__(self) -> str:
        """String representation."""
        return f"SolverModel(name={self.name}, type={self.solver_type}, executions={self.total_executions})"


class SolverResult(BaseModel, AuditMixin, MetadataMixin, StatusMixin):
    """Model for storing solver execution results."""

    __tablename__ = 'solver_results'

    # Execution identity
    solver_id = Column(Integer, ForeignKey('solvers.id'), nullable=False)
    execution_id = Column(String(255), nullable=False, unique=True)

    # Input data
    input_data = Column(JSON, nullable=False)
    input_parameters = Column(JSON, nullable=True)

    # Output data
    output_data = Column(JSON, nullable=True)
    solution = Column(JSON, nullable=True)  # The actual solution/result
    error_message = Column(Text, nullable=True)

    # Performance metrics
    execution_time_ms = Column(Float, nullable=False)
    memory_used_mb = Column(Float, nullable=True)
    iterations = Column(Integer, nullable=True)

    # Result validation
    is_valid_solution = Column(String(50), default='unknown', nullable=False)  # yes, no, unknown, partial
    convergence_criteria_met = Column(String(50), default='unknown', nullable=False)
    accuracy_achieved = Column(Float, nullable=True)

    # Execution context
    execution_started_at = Column(DateTime, nullable=False)
    execution_completed_at = Column(DateTime, nullable=True)

    # Relationships
    solver = relationship('SolverModel', back_populates='solver_results', foreign_keys=[solver_id])

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            'solver_id': self.solver_id,
            'execution_id': self.execution_id,
            'execution_time_ms': self.execution_time_ms,
            'is_valid_solution': self.is_valid_solution,
            'convergence_criteria_met': self.convergence_criteria_met,
        })
        return base_dict

    def __repr__(self) -> str:
        """String representation."""
        return f"SolverResult(execution_id={self.execution_id}, time={self.execution_time_ms}ms)"
