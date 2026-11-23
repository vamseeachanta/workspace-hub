"""
ABOUTME: Solver registry providing dynamic discovery, loading, and execution of solvers
ABOUTME: Implements registry pattern for 25+ mathematical solver modules
"""

import logging
from typing import Dict, Type, Optional, List
from importlib import import_module

from .base import BaseSolver, SolverResult

logger = logging.getLogger(__name__)


class SolverRegistry:
    """Central registry for managing all mathematical solvers."""

    def __init__(self):
        """Initialize solver registry."""
        self._solvers: Dict[str, BaseSolver] = {}
        self._solver_modules: Dict[str, str] = {}
        self._loader_config: Dict[str, Dict] = {}

    def register(self, name: str, solver: BaseSolver):
        """
        Register a solver instance.

        Args:
            name: Solver identifier
            solver: Solver instance
        """
        if not isinstance(solver, BaseSolver):
            raise TypeError(f"Solver must be instance of BaseSolver, got {type(solver)}")

        self._solvers[name] = solver
        logger.info(f"Registered solver: {name} ({solver})")

    def register_module(self, name: str, module_path: str, class_name: str):
        """
        Register a solver by module path (lazy loading).

        Args:
            name: Solver identifier
            module_path: Python module path (e.g., "solvers.stress.calculator")
            class_name: Class name in module
        """
        self._solver_modules[name] = (module_path, class_name)
        logger.info(f"Registered solver module: {name} -> {module_path}.{class_name}")

    def get(self, name: str) -> Optional[BaseSolver]:
        """
        Get solver by name, loading from module if necessary.

        Args:
            name: Solver identifier

        Returns:
            Solver instance or None if not found
        """
        # Check if already loaded
        if name in self._solvers:
            return self._solvers[name]

        # Try to load from module
        if name in self._solver_modules:
            module_path, class_name = self._solver_modules[name]
            try:
                module = import_module(module_path)
                solver_class: Type[BaseSolver] = getattr(module, class_name)
                solver = solver_class()
                self._solvers[name] = solver
                logger.info(f"Loaded solver: {name}")
                return solver
            except Exception as e:
                logger.error(f"Failed to load solver {name}: {e}")
                return None

        logger.warning(f"Solver not found: {name}")
        return None

    def list_solvers(self) -> List[str]:
        """Get list of all registered solver names."""
        all_solvers = set(self._solvers.keys()) | set(self._solver_modules.keys())
        return sorted(list(all_solvers))

    def list_loaded(self) -> List[str]:
        """Get list of currently loaded solver names."""
        return sorted(list(self._solvers.keys()))

    def solve(self, solver_name: str, parameters: Dict) -> Optional[SolverResult]:
        """
        Execute solver with given parameters.

        Args:
            solver_name: Name of solver to execute
            parameters: Solver parameters

        Returns:
            SolverResult or None if solver not found
        """
        solver = self.get(solver_name)
        if not solver:
            return None

        # Validate input
        valid, errors = solver.validate_input(parameters)
        if not valid:
            logger.error(f"Invalid input for {solver_name}: {errors}")
            result = solver._create_result(
                success=False,
                error_message=f"Invalid input: {', '.join(errors)}",
            )
            return result

        # Execute solver
        try:
            result = solver.solve(parameters)
            logger.info(f"Solver executed: {result}")
            return result
        except Exception as e:
            logger.error(f"Solver execution failed: {e}")
            return solver._create_result(
                success=False,
                error_message=str(e),
            )

    def batch_solve(self, jobs: List[tuple[str, Dict]]) -> List[SolverResult]:
        """
        Execute multiple solver jobs.

        Args:
            jobs: List of (solver_name, parameters) tuples

        Returns:
            List of SolverResult objects
        """
        results = []
        for solver_name, parameters in jobs:
            result = self.solve(solver_name, parameters)
            if result:
                results.append(result)

        logger.info(f"Batch solve completed: {len(results)} results")
        return results

    def get_solver_info(self, name: str) -> Optional[Dict]:
        """
        Get information about solver.

        Args:
            name: Solver name

        Returns:
            Dictionary of solver information or None
        """
        solver = self.get(name)
        if not solver:
            return None

        return {
            "name": solver.name,
            "version": solver.version,
            "class": solver.__class__.__name__,
            "accuracy_tolerance": solver.accuracy_tolerance,
        }

    def get_all_info(self) -> Dict[str, Dict]:
        """Get information about all registered solvers."""
        info = {}
        for name in self.list_solvers():
            solver_info = self.get_solver_info(name)
            if solver_info:
                info[name] = solver_info

        return info

    def clear(self):
        """Clear all registered solvers."""
        self._solvers.clear()
        self._solver_modules.clear()
        logger.info("Solver registry cleared")

    def __repr__(self) -> str:
        """String representation."""
        return f"SolverRegistry(loaded={len(self._solvers)}, registered={len(self._solver_modules)})"

    def __len__(self) -> int:
        """Return number of registered solvers."""
        return len(self._solvers) + len(self._solver_modules)
