"""
ABOUTME: Base solver class defining interface for all mathematical solvers
ABOUTME: Provides standardized execution, validation, and error handling
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging
import time

logger = logging.getLogger(__name__)


@dataclass
class SolverResult:
    """Result from solver execution."""

    success: bool
    solver_name: str
    execution_time_ms: float
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    warnings: list[str] = None

    def __post_init__(self):
        """Initialize warnings list if not provided."""
        if self.warnings is None:
            self.warnings = []

    def __repr__(self) -> str:
        """String representation."""
        status = "✓ SUCCESS" if self.success else "✗ FAILED"
        return f"SolverResult({self.solver_name}, {status}, {self.execution_time_ms:.2f}ms)"


class BaseSolver(ABC):
    """Base class for all mathematical solvers."""

    def __init__(self, name: str, version: str = "1.0.0", accuracy_tolerance: float = 0.001):
        """
        Initialize base solver.

        Args:
            name: Solver name
            version: Solver version
            accuracy_tolerance: Acceptable numerical accuracy tolerance (0.001 = 0.1%)
        """
        self.name = name
        self.version = version
        self.accuracy_tolerance = accuracy_tolerance
        self.logger = logging.getLogger(f"solvers.{name}")

    @abstractmethod
    def solve(self, parameters: Dict[str, Any]) -> SolverResult:
        """
        Execute solver with given parameters.

        Args:
            parameters: Dictionary of solver parameters

        Returns:
            SolverResult with success status and data
        """
        pass

    @abstractmethod
    def validate_input(self, parameters: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate solver input parameters.

        Args:
            parameters: Dictionary of parameters to validate

        Returns:
            Tuple of (valid: bool, errors: list[str])
        """
        pass

    def _execute_with_timing(self, solve_func, parameters: Dict[str, Any]) -> tuple[Dict[str, Any], float]:
        """
        Execute solver function and measure execution time.

        Args:
            solve_func: Callable to execute
            parameters: Parameters to pass to function

        Returns:
            Tuple of (result: dict, execution_time_ms: float)
        """
        start_time = time.time()
        result = solve_func(parameters)
        execution_time_ms = (time.time() - start_time) * 1000
        return result, execution_time_ms

    def _create_result(
        self,
        success: bool,
        result_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        execution_time_ms: float = 0.0,
        warnings: Optional[list[str]] = None,
    ) -> SolverResult:
        """
        Create standardized solver result.

        Args:
            success: Whether solver executed successfully
            result_data: Result data if successful
            error_message: Error message if failed
            execution_time_ms: Execution time in milliseconds
            warnings: List of warning messages

        Returns:
            SolverResult object
        """
        return SolverResult(
            success=success,
            solver_name=self.name,
            execution_time_ms=execution_time_ms,
            result_data=result_data,
            error_message=error_message,
            warnings=warnings or [],
        )

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(name={self.name}, version={self.version})"

    def __str__(self) -> str:
        """String representation."""
        return f"{self.name} v{self.version}"


class NumericalSolver(BaseSolver):
    """Base class for numerical solvers with convergence tolerance."""

    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        accuracy_tolerance: float = 0.001,
        max_iterations: int = 1000,
    ):
        """
        Initialize numerical solver.

        Args:
            name: Solver name
            version: Solver version
            accuracy_tolerance: Convergence tolerance
            max_iterations: Maximum iteration count
        """
        super().__init__(name, version, accuracy_tolerance)
        self.max_iterations = max_iterations

    def verify_accuracy(self, calculated: float, expected: float) -> bool:
        """
        Verify numerical accuracy within tolerance.

        Args:
            calculated: Calculated value
            expected: Expected value

        Returns:
            True if within tolerance
        """
        if expected == 0:
            return abs(calculated) < self.accuracy_tolerance

        relative_error = abs((calculated - expected) / expected)
        return relative_error <= self.accuracy_tolerance
