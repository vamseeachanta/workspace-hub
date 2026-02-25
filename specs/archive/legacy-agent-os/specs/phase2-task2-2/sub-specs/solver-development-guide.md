# Phase 2.2 Solver Development Guide

> Guide for implementing new solvers in the base_solvers framework
> Created: 2025-01-09
> Related: @.agent-os/specs/phase2-task2-2/spec.md, consolidation-strategy.md

## Quick Start: Create a New Solver in 5 Steps

### Step 1: Choose Base Class

```python
# For simple algorithms without configuration
from digitalmodel.base_solvers import BaseSolver

# For solvers with YAML configuration (RECOMMENDED)
from digitalmodel.base_solvers import ConfigurableSolver

# For domain analysis (results export, visualization)
from digitalmodel.base_solvers import AnalysisSolver
```

### Step 2: Define Configuration Schema

```python
from pydantic import BaseModel, Field

class MyLinearSolverConfig(BaseModel):
    """Configuration for my linear solver."""

    # Parameters with validation
    matrix_size: int = Field(
        ge=1,
        le=10000,
        description="Size of linear system"
    )
    tolerance: float = Field(
        gt=0,
        le=1e-2,
        description="Convergence tolerance"
    )
    max_iterations: int = Field(
        ge=1,
        le=1000,
        description="Maximum iterations"
    )
```

### Step 3: Create Solver Class

```python
class MyLinearSolver(ConfigurableSolver):
    """Solver for linear algebraic equations."""

    def __init__(self, config_path: Optional[str] = None):
        super().__init__(config_path)
        self.matrix = None
        self.solution = None

    def get_schema(self) -> Dict[str, Any]:
        """Return Pydantic schema for configuration."""
        return MyLinearSolverConfig.schema()

    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate solver inputs."""
        if 'A' not in inputs:
            raise SolverValidationError("Matrix A required")
        if 'b' not in inputs:
            raise SolverValidationError("Vector b required")

        A = inputs['A']
        b = inputs['b']

        # Validate matrix dimensions
        if len(A.shape) != 2:
            raise SolverValueError("Matrix A must be 2D")
        if A.shape[0] != A.shape[1]:
            raise SolverValueError("Matrix A must be square")
        if A.shape[0] != len(b):
            raise SolverValueError("Dimensions mismatch")

        return True

    def solve(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute solver algorithm."""
        try:
            self.validate_inputs(inputs)

            A = inputs['A']
            b = inputs['b']

            # Your algorithm here
            self.solution = np.linalg.solve(A, b)

            return {
                'success': True,
                'solution': self.solution,
                'residual': np.linalg.norm(A @ self.solution - b)
            }

        except np.linalg.LinAlgError as e:
            raise SolverExecutionError(f"Solver failed: {e}")

    def get_solver_metadata(self) -> SolverMetadata:
        """Return solver metadata."""
        return SolverMetadata(
            name="linear_solver",
            version="1.0.0",
            domain="linear_algebra",
            description="Solves linear system Ax=b",
            input_params=["A", "b"],
            output_params=["solution", "residual"]
        )
```

### Step 4: Create YAML Configuration

```yaml
# config/linear_algebra/linear_solver.yaml

solver:
  name: linear_solver
  version: "1.0.0"
  domain: linear_algebra
  description: Linear algebraic equation solver

parameters:
  matrix_size: 100
  tolerance: 1.0e-6
  max_iterations: 100
```

### Step 5: Write Tests

```python
import pytest
from digitalmodel.base_solvers.linear_algebra import MyLinearSolver

class TestMyLinearSolver:
    """Test suite for linear solver."""

    @pytest.fixture
    def solver(self):
        return MyLinearSolver(config_path="config/linear_algebra/linear_solver.yaml")

    def test_simple_2x2_system(self, solver):
        """Test solving simple 2x2 system."""
        A = np.array([[2, 1], [1, 3]], dtype=float)
        b = np.array([3, 5], dtype=float)

        result = solver.solve({'A': A, 'b': b})

        assert result['success']
        assert result['solution'].shape == (2,)
        assert result['residual'] < 1e-10

    def test_invalid_matrix_dimension(self, solver):
        """Test that solver rejects non-square matrices."""
        A = np.array([[1, 2, 3], [4, 5, 6]], dtype=float)  # 2x3
        b = np.array([1, 2], dtype=float)

        with pytest.raises(SolverValueError):
            solver.validate_inputs({'A': A, 'b': b})

    def test_dimension_mismatch(self, solver):
        """Test that solver rejects dimension mismatches."""
        A = np.array([[1, 2], [3, 4]], dtype=float)  # 2x2
        b = np.array([1, 2, 3], dtype=float)  # 3 elements

        with pytest.raises(SolverValueError):
            solver.validate_inputs({'A': A, 'b': b})
```

---

## Detailed Implementation Patterns

### Pattern 1: Configuration-Based Solver

**Best for:** Solvers with many parameters, YAML configuration

```python
from digitalmodel.base_solvers import ConfigurableSolver
from pydantic import BaseModel, Field

class CatenaaryConfig(BaseModel):
    """Configuration for catenary riser solver."""
    material_outer_diameter: float = Field(ge=0.01, le=2.0, description="Outer diameter (m)")
    material_wall_thickness: float = Field(ge=0.001, le=0.5)
    material_steel_density: float = Field(ge=7000, le=8000)
    water_depth: float = Field(ge=10, le=3000, description="Water depth (m)")
    wave_height_hs: float = Field(ge=0, le=15)
    wave_period: float = Field(ge=2, le=25)

class CatenaaryRiserSolver(ConfigurableSolver):
    """Catenary riser analysis solver."""

    def __init__(self, config_path: Optional[str] = None):
        super().__init__(config_path)
        # Parse config if provided
        if self.config:
            self._setup_from_config()

    def _setup_from_config(self):
        """Setup solver parameters from configuration."""
        self.od = self.config.material_outer_diameter
        self.wall_t = self.config.material_wall_thickness
        self.steel_density = self.config.material_steel_density
        self.water_depth = self.config.water_depth

    def get_schema(self) -> Dict[str, Any]:
        return CatenaaryConfig.schema()

    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate catenary analysis inputs."""
        required_keys = ['touchdown_tension', 'top_tension', 'line_weight']
        for key in required_keys:
            if key not in inputs:
                raise SolverValidationError(f"Missing required input: {key}")

        # Validate value ranges
        if inputs['touchdown_tension'] < 0:
            raise SolverValueError("Tension cannot be negative")

        return True

    def solve(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute catenary analysis."""
        try:
            self.validate_inputs(inputs)

            # Catenary algorithm
            s_values = self._calculate_arc_length(inputs)
            x_coords = self._calculate_x_coordinates(s_values)
            y_coords = self._calculate_y_coordinates(s_values)

            return {
                'arc_length': s_values,
                'x_coordinates': x_coords,
                'y_coordinates': y_coords,
                'touchdown_point': (x_coords[-1], y_coords[-1])
            }

        except Exception as e:
            raise SolverExecutionError(f"Catenary analysis failed: {e}")

    def get_solver_metadata(self) -> SolverMetadata:
        return SolverMetadata(
            name="catenary_riser",
            version="1.0.0",
            domain="marine",
            description="Catenary riser static analysis"
        )
```

### Pattern 2: Analysis Solver with Results Export

**Best for:** Solvers that produce detailed results for export/visualization

```python
from digitalmodel.base_solvers import AnalysisSolver
from dataclasses import dataclass

@dataclass
class StressAnalysisResults:
    """Container for stress analysis results."""
    von_mises_stress: np.ndarray
    principal_stresses: np.ndarray
    stress_intensity: np.ndarray
    max_stress: float
    min_stress: float

    def export(self, format: str, path: str):
        """Export results to file."""
        if format == 'json':
            self._export_json(path)
        elif format == 'csv':
            self._export_csv(path)
        else:
            raise ValueError(f"Unsupported format: {format}")

class VonMisesSolver(AnalysisSolver):
    """Von Mises stress analysis solver."""

    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate stress tensor inputs."""
        if 'stress_tensor' not in inputs:
            raise SolverValidationError("Stress tensor required")

        tensor = inputs['stress_tensor']
        if tensor.shape != (3, 3):
            raise SolverValueError("Stress tensor must be 3x3")

        return True

    def solve(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Von Mises stress."""
        try:
            self.validate_inputs(inputs)

            stress = inputs['stress_tensor']

            # Von Mises calculation
            von_mises = self._calculate_von_mises(stress)
            principal = self._calculate_principal_stresses(stress)

            # Store results
            self._last_result = StressAnalysisResults(
                von_mises_stress=von_mises,
                principal_stresses=principal,
                stress_intensity=self._calculate_intensity(principal),
                max_stress=np.max(von_mises),
                min_stress=np.min(von_mises)
            )

            return {
                'success': True,
                'von_mises_stress': von_mises,
                'principal_stresses': principal
            }

        except Exception as e:
            raise SolverExecutionError(f"Von Mises calculation failed: {e}")

    def get_solver_metadata(self) -> SolverMetadata:
        return SolverMetadata(
            name="von_mises_stress",
            version="1.0.0",
            domain="structural",
            description="Von Mises stress calculation for multiaxial stress states"
        )
```

### Pattern 3: Solver with Input/Output Converters

**Best for:** Solvers dealing with different unit systems

```python
from digitalmodel.base_solvers import ConfigurableSolver
from digitalmodel.base_solvers.utils import UnitConverter

class HydrodynamicSolver(ConfigurableSolver):
    """Hydrodynamic coefficient solver."""

    def __init__(self, config_path: Optional[str] = None, units: str = "SI"):
        super().__init__(config_path)
        self.unit_converter = UnitConverter(input_units=units, output_units="SI")

    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate hydrodynamic inputs."""
        # Convert inputs to SI units
        if 'diameter' in inputs:
            inputs['diameter'] = self.unit_converter.convert_length(inputs['diameter'])

        return True

    def solve(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate hydrodynamic coefficients."""
        try:
            self.validate_inputs(inputs)

            # Hydrodynamic calculations in SI units
            results = self._calculate_coefficients(inputs)

            # Convert back to original units if needed
            return {
                'cd': results['cd'],
                'added_mass_coefficient': results['added_mass'],
                'damping_coefficient': results['damping']
            }

        except Exception as e:
            raise SolverExecutionError(f"Hydrodynamic calculation failed: {e}")
```

### Pattern 4: Iterative Solver with Convergence Tracking

**Best for:** Solvers with iterative algorithms

```python
class IterativeSolver(ConfigurableSolver):
    """Base class for iterative solvers."""

    def __init__(self, config_path: Optional[str] = None):
        super().__init__(config_path)
        self.iteration_history = []
        self.converged = False

    def solve(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute iterative algorithm."""
        try:
            self.validate_inputs(inputs)
            self.iteration_history = []

            x = inputs.get('initial_guess', self._get_default_guess())

            for iteration in range(self.config.max_iterations):
                # Compute residual
                residual = self._compute_residual(x)
                self.iteration_history.append(residual)

                # Check convergence
                if residual < self.config.tolerance:
                    self.converged = True
                    break

                # Update guess
                x = self._update_solution(x)

            if not self.converged:
                raise SolverConvergenceError(
                    f"Failed to converge after {self.config.max_iterations} iterations"
                )

            return {
                'solution': x,
                'residual': residual,
                'iterations': len(self.iteration_history),
                'convergence_history': self.iteration_history
            }

        except Exception as e:
            raise SolverExecutionError(f"Iterative solver failed: {e}")

    def _compute_residual(self, x):
        """Compute residual for convergence check."""
        raise NotImplementedError

    def _update_solution(self, x):
        """Update solution for next iteration."""
        raise NotImplementedError
```

---

## Configuration Schema Guide

### Field Validation

```python
from pydantic import BaseModel, Field, validator

class SolverConfigExample(BaseModel):
    """Example configuration with various validations."""

    # Simple numeric fields with constraints
    matrix_size: int = Field(ge=1, le=10000)
    tolerance: float = Field(gt=0, le=0.1)
    iterations: int = Field(ge=1, le=1000)

    # Optional fields
    output_path: Optional[str] = None

    # Choice fields (enum)
    algorithm: str = Field(default="direct")

    # Custom validation
    @validator('matrix_size')
    def matrix_size_power_of_2(cls, v):
        import math
        if v & (v - 1) != 0:
            raise ValueError('Matrix size must be power of 2')
        return v

    @validator('tolerance')
    def tolerance_not_too_tight(cls, v):
        if v < 1e-15:
            raise ValueError('Tolerance too tight (< 1e-15)')
        return v
```

### YAML to Pydantic Mapping

```yaml
# config/example/solver.yaml
solver:
  name: example_solver
  version: "1.0.0"

parameters:
  matrix_size: 1024          # int
  tolerance: 1.0e-6          # float
  algorithm: "iterative"     # string (choice)
  output_path: null          # Optional[str]
```

```python
# Load and validate
class ExampleSolverConfig(BaseModel):
    matrix_size: int = Field(ge=1)
    tolerance: float = Field(gt=0)
    algorithm: str  # or Literal["direct", "iterative"]
    output_path: Optional[str] = None

# Pydantic automatically validates YAML data
config = ExampleSolverConfig(**yaml_data['parameters'])
```

---

## Testing Patterns for Solvers

### Test Structure

```python
import pytest
import numpy as np
from digitalmodel.base_solvers import MySolver

class TestMySolver:
    """Test suite for my solver."""

    @pytest.fixture
    def solver(self):
        """Create solver instance."""
        return MySolver(config_path="config/domain/solver.yaml")

    @pytest.fixture
    def sample_data(self):
        """Load sample test data."""
        return {
            'input1': np.array([1, 2, 3]),
            'input2': np.array([4, 5, 6])
        }

    # 1. VALIDATION TESTS

    def test_validate_inputs_success(self, solver, sample_data):
        """Test valid inputs pass validation."""
        assert solver.validate_inputs(sample_data)

    def test_validate_missing_required_field(self, solver):
        """Test that missing required field raises error."""
        with pytest.raises(SolverValidationError):
            solver.validate_inputs({'input1': [1, 2, 3]})

    def test_validate_invalid_type(self, solver):
        """Test that invalid type raises error."""
        with pytest.raises(SolverTypeError):
            solver.validate_inputs({'input1': "not an array"})

    def test_validate_value_out_of_range(self, solver):
        """Test that out-of-range value raises error."""
        with pytest.raises(SolverValueError):
            solver.validate_inputs({'parameter': -1})  # if should be > 0

    # 2. ALGORITHM TESTS

    def test_solve_simple_case(self, solver, sample_data):
        """Test solver on simple known case."""
        result = solver.solve(sample_data)
        assert result['success']
        # Verify known result
        expected = np.array([5, 7, 9])
        np.testing.assert_array_almost_equal(result['output'], expected)

    def test_solve_boundary_case(self, solver):
        """Test solver on boundary conditions."""
        data = {'input': np.array([0, 0, 0])}
        result = solver.solve(data)
        assert result['success']

    def test_solve_convergence(self, solver):
        """Test that iterative solver converges."""
        result = solver.solve({'initial_guess': [1, 1, 1]})
        assert result['success']
        assert result['iterations'] < solver.config.max_iterations

    # 3. ERROR HANDLING TESTS

    def test_solve_raises_execution_error_on_failure(self, solver):
        """Test that solver raises error on failure."""
        with pytest.raises(SolverExecutionError):
            solver.solve({'invalid': 'data'})

    def test_convergence_failure(self, solver):
        """Test convergence error for non-converging system."""
        with pytest.raises(SolverConvergenceError):
            solver.solve({'ill_conditioned': True})

    # 4. PERFORMANCE TESTS

    @pytest.mark.benchmark
    def test_performance_acceptable(self, solver, benchmark, sample_data):
        """Test that solver performs within target time."""
        result = benchmark(solver.solve, sample_data)
        assert result['success']

    # 5. METADATA TESTS

    def test_get_solver_metadata(self, solver):
        """Test that solver returns valid metadata."""
        metadata = solver.get_solver_metadata()
        assert metadata.name == 'expected_name'
        assert metadata.version == '1.0.0'
        assert metadata.domain == 'expected_domain'
```

### Test Fixtures

```python
# tests/fixtures/solver_fixtures.py

@pytest.fixture(scope="session")
def marine_solver_data():
    """Marine solver test data."""
    return {
        'catenary': np.load('tests/fixtures/marine/catenary_data.npy'),
        'hydrodynamic': pd.read_csv('tests/fixtures/marine/hydro_data.csv')
    }

@pytest.fixture(scope="session")
def structural_solver_data():
    """Structural solver test data."""
    return {
        'stress_tensors': np.load('tests/fixtures/structural/stress_tensors.npy'),
        'loads': pd.read_csv('tests/fixtures/structural/loads.csv')
    }
```

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Not Validating Inputs

```python
# WRONG
def solve(self, inputs):
    return {'result': inputs['data'] * 2}  # Assumes 'data' exists

# RIGHT
def solve(self, inputs):
    self.validate_inputs(inputs)
    return {'result': inputs['data'] * 2}
```

### ❌ Mistake 2: Generic Exception Handling

```python
# WRONG
def solve(self, inputs):
    try:
        # algorithm
    except:
        raise Exception("Failed")

# RIGHT
def solve(self, inputs):
    try:
        # algorithm
    except ZeroDivisionError:
        raise SolverValueError("Division by zero - check input data")
    except np.linalg.LinAlgError:
        raise SolverExecutionError("Algorithm failed - ill-conditioned matrix")
```

### ❌ Mistake 3: Inconsistent Return Format

```python
# WRONG
# Sometimes returns dict, sometimes returns ndarray
def solve(self, inputs):
    if self.simple:
        return result_array
    return {'result': result_array}

# RIGHT
# Always return same format
def solve(self, inputs):
    return {
        'success': True,
        'result': result_array,
        'metadata': {...}
    }
```

### ❌ Mistake 4: No Configuration Schema

```python
# WRONG
class Solver:
    def __init__(self, **kwargs):
        self.params = kwargs  # No validation

# RIGHT
class Solver(ConfigurableSolver):
    def get_schema(self):
        return SolverConfig.schema()  # Pydantic validates
```

### ❌ Mistake 5: Missing Error Cases in Tests

```python
# WRONG - only tests happy path
def test_solve():
    result = solver.solve(good_input)
    assert result['success']

# RIGHT - tests multiple scenarios
def test_solve_valid_input():
    result = solver.solve(good_input)
    assert result['success']

def test_solve_missing_input():
    with pytest.raises(SolverValidationError):
        solver.solve({})

def test_solve_invalid_type():
    with pytest.raises(SolverTypeError):
        solver.solve({'data': 'string'})

def test_solve_out_of_range():
    with pytest.raises(SolverValueError):
        solver.solve({'parameter': -1})
```

---

## Integration with Phase 2.1 ConfigManager

### Using ConfigManager for Solver Configuration

```python
from digitalmodel.phase2.config_manager import ConfigManager

# Load configuration
config_mgr = ConfigManager()
solver_config = config_mgr.load_solver_config(
    domain='marine',
    solver_name='catenary'
)

# Use with solver
solver = CatenaaryRiser(config=solver_config)
result = solver.solve(inputs)
```

### Saving Solver Configurations

```python
# Save validated configuration
config_mgr.save_solver_config(
    domain='marine',
    solver_name='catenary',
    config=my_config
)
```

---

## Domain-Specific Examples

### Marine Engineering: Catenary Solver

See `/mnt/github/workspace-hub/.agent-os/specs/phase2-task2-2/examples/marine_catenary_solver.py`

### Structural Analysis: Von Mises Solver

See `/mnt/github/workspace-hub/.agent-os/specs/phase2-task2-2/examples/structural_vonmises_solver.py`

### Fatigue Analysis: S-N Curves Solver

See `/mnt/github/workspace-hub/.agent-os/specs/phase2-task2-2/examples/fatigue_sn_curves_solver.py`

### Signal Processing: FFT Solver

See `/mnt/github/workspace-hub/.agent-os/specs/phase2-task2-2/examples/signal_fft_solver.py`

---

## Performance Optimization Tips

### Tip 1: Pre-compute in Constructor

```python
# WRONG - recompute every time
def solve(self, inputs):
    material_props = self._load_material_properties()
    ...

# RIGHT - compute once
def __init__(self, config_path):
    super().__init__(config_path)
    self.material_props = self._load_material_properties()

def solve(self, inputs):
    # Use pre-computed properties
    ...
```

### Tip 2: Vectorize Numpy Operations

```python
# WRONG - loop in Python
result = []
for i in range(len(data)):
    result.append(data[i] * 2)

# RIGHT - use NumPy vectorization
result = data * 2
```

### Tip 3: Cache Expensive Computations

```python
from functools import lru_cache

class SolverWithCache(ConfigurableSolver):
    @lru_cache(maxsize=32)
    def _expensive_computation(self, param1, param2):
        # Cached result
        return np.sqrt(param1**2 + param2**2)
```

---

## Checklist: Before Submitting a New Solver

- [ ] Solver inherits from `BaseSolver` or `ConfigurableSolver`
- [ ] All abstract methods implemented (`validate_inputs`, `solve`, `get_solver_metadata`)
- [ ] YAML configuration file created in `config/[domain]/[solver_name].yaml`
- [ ] Configuration schema defined with Pydantic validation
- [ ] Error handling uses `SolverError` hierarchy
- [ ] 8-10 comprehensive tests written (validation + algorithm + errors)
- [ ] 90%+ test coverage achieved
- [ ] Performance benchmarks recorded and acceptable
- [ ] Documentation complete with docstrings
- [ ] No breaking changes to existing API
- [ ] All tests passing: `pytest tests/unit/base_solvers/`

---

**Next Steps:**

1. Choose a solver to implement from the consolidation list
2. Follow the patterns above
3. Write tests before implementation (TDD)
4. Achieve 90%+ coverage
5. Register solver in domain `__init__.py`
6. Submit for review

