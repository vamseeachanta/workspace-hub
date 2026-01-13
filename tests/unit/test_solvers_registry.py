"""
ABOUTME: Unit tests for SolverRegistry and solver management
ABOUTME: Tests registration, lazy loading, batch execution, and error handling
"""

import pytest
from unittest.mock import MagicMock, patch

from src.solvers.base import BaseSolver, SolverResult, NumericalSolver
from src.solvers.registry import SolverRegistry


class MockSolver(BaseSolver):
    """Mock solver for testing."""

    def __init__(self, name="test_solver", should_fail=False):
        super().__init__(name=name)
        self.should_fail = should_fail

    def solve(self, parameters):
        """Mock solve implementation."""
        if self.should_fail:
            return self._create_result(
                success=False,
                error_message="Mock solver error"
            )

        return self._create_result(
            success=True,
            result_data={'result': parameters.get('value', 0) * 2},
            execution_time_ms=10.5
        )

    def validate_input(self, parameters):
        """Mock input validation."""
        if 'value' not in parameters:
            return False, ['Missing required parameter: value']
        if not isinstance(parameters['value'], (int, float)):
            return False, ['Parameter value must be numeric']
        return True, []


class MockNumericalSolver(NumericalSolver):
    """Mock numerical solver for testing."""

    def __init__(self):
        super().__init__(name="numerical_test")

    def solve(self, parameters):
        """Mock solve implementation."""
        calculated = parameters.get('calculated', 0)
        expected = parameters.get('expected', 1)

        if self.verify_accuracy(calculated, expected):
            return self._create_result(success=True)
        else:
            return self._create_result(
                success=False,
                error_message="Accuracy verification failed"
            )

    def validate_input(self, parameters):
        """Mock input validation."""
        required = ['calculated', 'expected']
        missing = [p for p in required if p not in parameters]

        if missing:
            return False, [f'Missing parameters: {missing}']
        return True, []


class TestSolverRegistry:
    """Test SolverRegistry functionality."""

    @pytest.fixture
    def registry(self):
        """Create a fresh registry for each test."""
        return SolverRegistry()

    def test_register_solver(self, registry):
        """Test registering a solver instance."""
        solver = MockSolver()
        registry.register('mock_solver', solver)

        assert 'mock_solver' in registry.list_solvers()

    def test_register_multiple_solvers(self, registry):
        """Test registering multiple solvers."""
        solver1 = MockSolver('solver1')
        solver2 = MockSolver('solver2')

        registry.register('solver1', solver1)
        registry.register('solver2', solver2)

        solvers = registry.list_solvers()
        assert 'solver1' in solvers
        assert 'solver2' in solvers
        assert len(solvers) == 2

    def test_register_module(self, registry):
        """Test registering a solver by module path (lazy loading)."""
        registry.register_module('stress_calc', 'solvers.stress.calculator', 'StressCalculator')

        assert 'stress_calc' in registry.list_solvers()
        # Should not be in loaded list yet
        assert 'stress_calc' not in registry.list_loaded()

    def test_get_registered_solver(self, registry):
        """Test retrieving a registered solver."""
        solver = MockSolver()
        registry.register('test_solver', solver)

        retrieved = registry.get('test_solver')
        assert retrieved is solver

    def test_get_nonexistent_solver(self, registry):
        """Test getting non-existent solver returns None."""
        result = registry.get('nonexistent')
        assert result is None

    def test_list_all_solvers(self, registry):
        """Test listing all registered solvers."""
        solver1 = MockSolver('solver1')
        solver2 = MockSolver('solver2')

        registry.register('solver1', solver1)
        registry.register('solver2', solver2)
        registry.register_module('solver3', 'module.path', 'Solver3')

        solvers = registry.list_solvers()
        assert len(solvers) >= 3
        assert 'solver1' in solvers
        assert 'solver2' in solvers
        assert 'solver3' in solvers

    def test_list_loaded_solvers(self, registry):
        """Test listing only loaded solvers."""
        solver1 = MockSolver('solver1')
        solver2 = MockSolver('solver2')

        registry.register('solver1', solver1)
        registry.register('solver2', solver2)
        registry.register_module('solver3', 'module.path', 'Solver3')

        loaded = registry.list_loaded()
        assert 'solver1' in loaded
        assert 'solver2' in loaded
        assert 'solver3' not in loaded

    def test_solve_with_valid_input(self, registry):
        """Test solving with valid input."""
        solver = MockSolver()
        registry.register('test_solver', solver)

        result = registry.solve('test_solver', {'value': 5})

        assert result is not None
        assert result.success is True
        assert result.result_data['result'] == 10

    def test_solve_with_invalid_input(self, registry):
        """Test solving with invalid input."""
        solver = MockSolver()
        registry.register('test_solver', solver)

        result = registry.solve('test_solver', {})

        assert result is not None
        assert result.success is False
        assert 'Missing required parameter' in result.error_message

    def test_solve_nonexistent_solver(self, registry):
        """Test solving with non-existent solver."""
        result = registry.solve('nonexistent', {})

        assert result is None

    def test_batch_solve(self, registry):
        """Test executing multiple solver jobs."""
        solver1 = MockSolver('solver1')
        solver2 = MockSolver('solver2')

        registry.register('solver1', solver1)
        registry.register('solver2', solver2)

        jobs = [
            ('solver1', {'value': 1}),
            ('solver2', {'value': 2}),
            ('solver1', {'value': 3}),
        ]

        results = registry.batch_solve(jobs)

        assert len(results) == 3
        assert results[0].result_data['result'] == 2
        assert results[1].result_data['result'] == 4
        assert results[2].result_data['result'] == 6

    def test_get_solver_info(self, registry):
        """Test retrieving solver information."""
        solver = MockSolver(name='info_test')
        registry.register('test_solver', solver)

        info = registry.get_solver_info('test_solver')

        assert info is not None
        assert info['name'] == 'info_test'
        assert info['version'] == '1.0.0'
        assert info['class'] == 'MockSolver'

    def test_get_all_info(self, registry):
        """Test retrieving information for all solvers."""
        solver1 = MockSolver(name='solver1')
        solver2 = MockSolver(name='solver2')

        registry.register('solver1', solver1)
        registry.register('solver2', solver2)

        all_info = registry.get_all_info()

        assert 'solver1' in all_info
        assert 'solver2' in all_info
        assert all_info['solver1']['name'] == 'solver1'

    def test_clear_registry(self, registry):
        """Test clearing all registered solvers."""
        solver1 = MockSolver()
        solver2 = MockSolver()

        registry.register('solver1', solver1)
        registry.register('solver2', solver2)

        assert len(registry.list_solvers()) >= 2

        registry.clear()

        assert len(registry.list_solvers()) == 0

    def test_solver_with_execution_time(self, registry):
        """Test that solver result includes execution time."""
        solver = MockSolver()
        registry.register('test_solver', solver)

        result = registry.solve('test_solver', {'value': 10})

        assert result.execution_time_ms >= 0

    def test_solver_error_handling(self, registry):
        """Test handling solver execution errors."""
        solver = MockSolver(should_fail=True)
        registry.register('failing_solver', solver)

        result = registry.solve('failing_solver', {'value': 5})

        assert result.success is False
        assert result.error_message is not None

    def test_registry_repr(self, registry):
        """Test string representation of registry."""
        solver1 = MockSolver()
        registry.register('solver1', solver1)
        registry.register_module('solver2', 'module', 'Solver2')

        repr_str = repr(registry)
        assert 'SolverRegistry' in repr_str
        assert 'loaded=1' in repr_str
        assert 'registered=1' in repr_str

    def test_numerical_solver_accuracy_verification(self):
        """Test numerical solver accuracy verification."""
        solver = MockNumericalSolver()

        # Test within tolerance
        result = solver.solve({'calculated': 1.0009, 'expected': 1.0})
        assert result.success is True

        # Test outside tolerance
        result = solver.solve({'calculated': 1.1, 'expected': 1.0})
        assert result.success is False

    def test_numerical_solver_zero_expected(self):
        """Test numerical solver with zero expected value."""
        solver = MockNumericalSolver()

        # When expected is 0, checks if calculated < tolerance
        result = solver.solve({'calculated': 0.0001, 'expected': 0})
        assert result.success is True

        result = solver.solve({'calculated': 0.002, 'expected': 0})
        assert result.success is False
