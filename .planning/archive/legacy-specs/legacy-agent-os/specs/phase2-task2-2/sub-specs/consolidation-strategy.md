# Phase 2.2 Mathematical Solvers Consolidation Strategy

> Technical Architecture & Implementation Strategy
> Created: 2025-01-09
> Related Spec: @.agent-os/specs/phase2-task2-2/spec.md

## Executive Summary

This document defines the technical architecture and implementation phasing for consolidating 30+ mathematical solver modules into a unified base_solvers framework. The strategy emphasizes:

1. **Unified Interface Pattern:** All solvers inherit from `BaseSolver` or domain-specific abstractions
2. **Configuration Management:** Integration with Phase 2.1 ConfigManager for YAML-based configuration
3. **Phased Migration:** Six implementation phases enabling parallel work and staged testing
4. **Backward Compatibility:** Existing solver APIs maintained during transition
5. **Comprehensive Testing:** 90%+ coverage with domain-specific test suites

---

## Unified Solver Interface Design

### Core Architecture

```
┌─────────────────────────────────────────────────────────┐
│              SolverRegistry                             │
│  - Discover and instantiate solvers by name/domain     │
│  - Maintain metadata and versioning                     │
└─────────────────────────────────────────────────────────┘
                         ▲
                         │
    ┌────────────────────┴────────────────────┐
    │                                         │
┌───────────────┐                  ┌──────────────────┐
│  BaseSolver   │                  │ConfigurableSolver│
│               │                  │                  │
│ - validate_   │                  │ + load_config()  │
│   inputs()    │                  │ + save_config()  │
│ - solve()     │                  │ + get_schema()   │
│ - get_meta    │                  └──────────────────┘
│   data()      │                         ▲
│ - reset()     │                         │
└───────────────┘                         │
        ▲                    ┌────────────┴────────────┐
        │                    │                         │
┌───────┴──────────┐   ┌─────────────────┐    ┌──────────────┐
│AnalysisSolver    │   │MarineSolver     │    │SignalSolver  │
│                  │   │                 │    │              │
│ + get_results()  │   │ + get_units()   │    │ + get_freq() │
│ + export()       │   │ + validate_env()│    │ + get_fft()  │
└───────┬──────────┘   └─────────────────┘    └──────────────┘
        │
    ┌───┴────────────────────────────────────┐
    │                                        │
┌──────────────┐  ┌──────────────┐  ┌────────────┐
│StressSolver  │  │BucklingSlver │  │FatigueSolv │
│              │  │              │  │            │
│ + von_mises()│  │ + euler_load()   │ + damage()   │
│ + get_units()│  │ + buckling_mode()│ + life()    │
└──────────────┘  └──────────────┘  └────────────┘
```

### BaseSolver Abstract Base Class

```python
class BaseSolver(ABC):
    """Abstract base class for all mathematical solvers."""

    @abstractmethod
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """
        Validate solver inputs against schema.

        Args:
            inputs: Input dictionary to validate

        Returns:
            True if valid, raises SolverError if invalid

        Raises:
            SolverValidationError: Input validation failed
            SolverTypeError: Type mismatch
            SolverValueError: Value out of valid range
        """
        pass

    @abstractmethod
    def solve(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute solver algorithm.

        Args:
            inputs: Validated input dictionary

        Returns:
            Dictionary with solution results

        Raises:
            SolverExecutionError: Solver algorithm failed
            SolverConvergenceError: Algorithm did not converge
        """
        pass

    @abstractmethod
    def get_solver_metadata(self) -> SolverMetadata:
        """
        Return solver metadata (name, version, domain, capabilities).

        Returns:
            SolverMetadata object with solver information
        """
        pass

    def reset(self) -> None:
        """Reset solver to initial state."""
        self._last_result = None
        self._validation_errors = []
```

### ConfigurableSolver for YAML Configuration

```python
class ConfigurableSolver(BaseSolver):
    """Base class for solvers with YAML configuration."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize solver with optional configuration file.

        Args:
            config_path: Path to YAML configuration file
        """
        super().__init__()
        self.config = None
        if config_path:
            self.load_config(config_path)

    def load_config(self, config_path: str) -> None:
        """Load configuration from YAML file."""
        config_data = ConfigManager.load_yaml(config_path)
        self.config = self._parse_config(config_data)

    def save_config(self, output_path: str) -> None:
        """Save current configuration to YAML file."""
        if not self.config:
            raise SolverConfigError("No configuration loaded")
        ConfigManager.save_yaml(output_path, self.config.dict())

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Return Pydantic schema for configuration validation."""
        pass

    def _parse_config(self, data: Dict) -> BaseModel:
        """Parse and validate configuration data."""
        schema = self.get_schema()
        return schema(**data)
```

### AnalysisSolver for Domain Analysis

```python
class AnalysisSolver(ConfigurableSolver):
    """Base class for analysis solvers (stress, fatigue, wave, etc.)."""

    def get_results(self) -> AnalysisResults:
        """
        Get last analysis results with metadata.

        Returns:
            AnalysisResults object with results and metadata
        """
        if not self._last_result:
            raise SolverExecutionError("No results available - run solve() first")
        return self._last_result

    def export(self, format: str, output_path: str) -> None:
        """
        Export results in specified format (JSON, CSV, HTML).

        Args:
            format: Export format ('json', 'csv', 'html')
            output_path: Path to save results
        """
        if not self._last_result:
            raise SolverExecutionError("No results to export")
        self._last_result.export(format, output_path)
```

### Error Handling Hierarchy

```python
class SolverError(Exception):
    """Base exception for all solver errors."""
    pass

class SolverValidationError(SolverError):
    """Input validation failed."""
    pass

class SolverTypeError(SolverValidationError):
    """Type mismatch in input."""
    pass

class SolverValueError(SolverValidationError):
    """Value out of valid range."""
    pass

class SolverConfigError(SolverError):
    """Configuration error."""
    pass

class SolverExecutionError(SolverError):
    """Solver algorithm execution failed."""
    pass

class SolverConvergenceError(SolverExecutionError):
    """Algorithm did not converge."""
    pass
```

---

## Configuration Schema Pattern

### Base Configuration Structure

All solvers follow this YAML pattern:

```yaml
# config/[domain]/[solver_name].yaml

solver:
  name: solver_identifier
  version: "1.0.0"
  domain: [marine|structural|fatigue|signal|specialized]
  description: Brief description of what solver does

parameters:
  # Domain-specific parameters
  # All must have type, range, units, description

schema:
  type: object
  properties:
    param1:
      type: number
      minimum: 0
      maximum: 1000
      description: Parameter description
      units: SI unit
  required: [param1, param2]
```

### Example: Catenary Riser Configuration

```yaml
solver:
  name: catenary_riser
  version: "1.0.0"
  domain: marine
  description: Catenary riser shape and tension analysis

parameters:
  material:
    outer_diameter: 0.5  # meters
    wall_thickness: 0.02
    steel_density: 7850  # kg/m³
    youngs_modulus: 210e9  # Pa

  geometry:
    water_depth: 1000  # meters
    tension_touchdown: true

  environmental:
    wave_height_hs: 2.5  # meters
    wave_period: 10.5  # seconds
    current_velocity: 1.2  # m/s
```

---

## Cross-Domain Dependency Management

### Dependency Graph

```
Marine Solvers
├── Catenary (standalone)
├── Hydrodynamic (standalone)
├── Environmental (standalone)
└── Wave Spectra (standalone)

Structural Solvers
├── Stress (standalone)
├── Buckling (depends on Stress for validation)
└── Multiaxial (depends on Stress)

Fatigue Solvers
├── S-N Curves (standalone - 221 curves)
├── Damage (depends on S-N Curves)
└── Integration (signal processing → fatigue)

Signal Processors
├── FFT (standalone)
├── Filtering (depends on FFT)
├── Spectral (depends on FFT)
└── Rainflow (depends on Signal)
    └── Connects to Fatigue Integration

Specialized Solvers
├── Mooring (depends on Catenary)
├── OrcaFlex (depends on Hydrodynamic, Environmental)
├── VIV (depends on Hydrodynamic, Structural)
├── RAO (depends on Hydrodynamic, Wave Spectra)
└── API Compliance (depends on Stress, Buckling)
```

### Dependency Resolution

**Strategy:** Phase implementation follows dependency order:

1. **Phase A:** Base infrastructure (no domain dependencies)
2. **Phase B:** Marine (independent)
3. **Phase C:** Structural/Fatigue (independent)
4. **Phase D:** Signal (can run parallel with B/C, minimal deps)
5. **Phase E:** Specialized (depends on B, C, D)
6. **Phase F:** Integration testing (all phases complete)

---

## Consolidation Phasing

### Phase A: Base Infrastructure (Week 1-2)

**Deliverables:**
- Abstract base classes and interfaces
- Configuration management integration
- Error handling hierarchy
- SolverRegistry for discovery

**Files Created:**
- `base.py` - BaseSolver, ConfigurableSolver, AnalysisSolver (250 lines)
- `interfaces.py` - Protocols and type hints (150 lines)
- `registry.py` - SolverRegistry implementation (200 lines)
- `exceptions.py` - Error hierarchy (100 lines)
- `config/solver_config.py` - Configuration utilities (150 lines)

**Tests:** 35+ tests for base infrastructure

**Blockers:** None (independent phase)

### Phase B: Marine Engineering Solvers (Week 1-3, parallel with A)

**Consolidate:**
1. **Catenary Riser Solver** (existing → base_solvers.marine.catenary)
   - Static shape analysis
   - Tension and forces
   - Touchdown point analysis
   - Tests: 10+ tests, validate I/O, algorithm, edge cases

2. **Hydrodynamic Coefficients Solver** (→ base_solvers.marine.hydrodynamic)
   - Added mass calculation
   - Damping coefficients
   - Drag forces
   - Tests: 10+ tests, verify coefficient ranges

3. **Environmental Loading Solver** (→ base_solvers.marine.environmental)
   - Wave loading (Airy theory, Stokes)
   - Current profile
   - Wind loading
   - Tests: 8+ tests, environmental conditions

4. **Wave Spectrum Solver** (→ base_solvers.marine.wave_spectra)
   - JONSWAP spectrum
   - Pierson-Moskowitz spectrum
   - Peak spectral density
   - Tests: 8+ tests, spectrum validation

**Configuration:** Create `config/marine/[solver].yaml` for each

**Tests:** 36+ marine solver tests, 90%+ coverage

**Dependencies:** Requires Phase A completion

**Parallelizable:** Yes - all marine solvers independent

### Phase C: Structural & Fatigue Solvers (Week 2-4, parallel with B)

**Consolidate:**

**Structural Solvers:**
1. **Von Mises Stress Solver** (→ base_solvers.structural.stress)
   - Multiaxial stress states
   - Principal stresses
   - Equivalent stress calculation
   - Tests: 10+ tests

2. **Buckling Analysis Solver** (→ base_solvers.structural.buckling)
   - Euler buckling
   - Reduced modulus method
   - Johnson formula
   - Tests: 10+ tests

3. **Multiaxial Stress Solver** (→ base_solvers.structural.multiaxial)
   - Combined stress states
   - Stress transformations
   - Tests: 8+ tests

**Fatigue Solvers:**
1. **S-N Curves Solver** (→ base_solvers.fatigue.sn_curves)
   - 221 curves from 17 international standards (DNV, API, BS, ABS, etc.)
   - Curve lookup and interpolation
   - Extrapolation handling
   - Tests: 12+ tests covering all standards

2. **Damage Accumulation Solver** (→ base_solvers.fatigue.damage)
   - Miner's rule
   - Non-linear cumulative damage
   - Life prediction
   - Tests: 10+ tests

3. **Fatigue Integration Solver** (→ base_solvers.fatigue.integration)
   - Signal cycle integration
   - Stress-life calculations
   - Tests: 8+ tests

**Configuration:** Create `config/structural/[solver].yaml` and `config/fatigue/[solver].yaml`

**Tests:** 58+ structural/fatigue tests, 90%+ coverage

**Dependencies:** Requires Phase A completion

**Parallelizable:** Yes - structural/fatigue independent of Phase B

### Phase D: Signal Processing Solvers (Week 3-4, can parallel with B/C)

**Consolidate:**
1. **FFT Solver** (→ base_solvers.signal.fft)
   - Fast Fourier Transform
   - Inverse FFT
   - Frequency domain conversion
   - Tests: 10+ tests

2. **Digital Filtering Solver** (→ base_solvers.signal.filtering)
   - Low-pass filter
   - High-pass filter
   - Band-pass filter
   - Tests: 10+ tests

3. **Spectral Analysis Solver** (→ base_solvers.signal.spectral)
   - Power spectral density
   - Frequency response
   - Spectral moments
   - Tests: 8+ tests

4. **Rainflow Cycle Counting Solver** (→ base_solvers.signal.rainflow)
   - ASTM E1049-85 algorithm
   - Cycle extraction
   - Peak-valley method
   - Tests: 10+ tests

**Configuration:** Create `config/signal/[solver].yaml` for each

**Tests:** 38+ signal solver tests, 90%+ coverage

**Dependencies:** Requires Phase A completion (minimal dependencies on B/C)

**Parallelizable:** Yes - can run parallel with Phases B and C

### Phase E: Specialized Domain Solvers (Week 4-5)

**Consolidate:**
1. **Mooring System Solver** (→ base_solvers.specialized.mooring)
   - CALM buoy mooring
   - SALM buoy mooring
   - Catenary leg analysis (uses Phase B)
   - Tests: 10+ tests
   - **Depends on:** Catenary solver (Phase B)

2. **OrcaFlex Solver** (→ base_solvers.specialized.orcaflex)
   - Model post-processing
   - Results extraction
   - Statistics calculation
   - Tests: 8+ tests
   - **Depends on:** Hydrodynamic, Environmental (Phase B)

3. **VIV Analysis Solver** (→ base_solvers.specialized.viv)
   - Vortex-induced vibration
   - Natural frequency calculation
   - Safety factor assessment
   - Tests: 8+ tests
   - **Depends on:** Hydrodynamic, Structural (Phase B, C)

4. **RAO Analysis Solver** (→ base_solvers.specialized.rao)
   - Response Amplitude Operator
   - Frequency response
   - Vessel motion calculation
   - Tests: 8+ tests
   - **Depends on:** Hydrodynamic, Wave Spectra (Phase B)

5. **API Compliance Solver** (→ base_solvers.specialized.api_compliance)
   - API 579 compliance
   - DNV standards verification
   - Safety factor checking
   - Tests: 6+ tests
   - **Depends on:** Stress, Buckling (Phase C)

**Configuration:** Create `config/specialized/[solver].yaml` for each

**Tests:** 40+ specialized solver tests, 90%+ coverage

**Dependencies:** Requires Phase B, C, D completion

**Blockers:** Cannot start until Phase B, C, D complete

### Phase F: Integration & Documentation (Week 5-6)

**Tasks:**
1. **Integration Testing** (10+ cross-solver tests)
   - Marine + Specialized workflows
   - Structural + Fatigue workflows
   - Signal + Fatigue workflows
   - Multi-solver pipelines

2. **Final Coverage Verification**
   - Achieve 90%+ coverage across all solvers
   - Document any coverage gaps
   - Add missing test cases

3. **Documentation Completion**
   - Solver development guide with templates
   - Migration guide from old patterns
   - API reference complete
   - Configuration guide

4. **Git Operations**
   - Commit all new code
   - Create pull request
   - Merge to main

**Tests:** 10+ integration tests

**Final Metrics:**
- 190+ total tests
- 90%+ coverage
- All solvers migrated
- All documentation complete

---

## Testing Strategy by Domain

### Marine Engineering Testing

**Catenary Riser Tests:**
- Verify static shape calculation
- Validate tension distribution
- Test touchdown point detection
- Validate forces (horizontal, vertical, bending)
- Edge cases: shallow water, steep angles
- Benchmark: < 100ms for 1000-point analysis

**Hydrodynamic Testing:**
- Verify added mass calculations
- Validate damping coefficients
- Test drag force computation
- Compare with industry standards (DNV, API)
- Benchmark: < 50ms for single point

**Environmental Testing:**
- Test wave loading calculations
- Verify current profile application
- Test wind load computation
- Boundary conditions: zero velocity, max conditions

**Wave Spectrum Testing:**
- JONSWAP vs Pierson-Moskowitz accuracy
- Peak period validation
- Spectral moment calculations
- Validate spectrum integration

### Structural & Fatigue Testing

**Von Mises Stress Testing:**
- Uniaxial stress cases (verify direct output)
- Multiaxial stress states (verify transformation)
- Principal stress calculations
- Edge cases: zero stress, equal stresses

**Buckling Testing:**
- Euler formula verification
- Reduced modulus method
- Johnson formula
- Critical load calculation
- Validate buckling modes

**S-N Curves Testing:**
- Test all 221 curves (17 standards)
- Interpolation accuracy
- Extrapolation handling
- Stress range validation
- Life calculation accuracy

**Damage Testing:**
- Miner's rule validation (∑Ni/Nfi)
- Non-linear damage models
- Cumulative damage sequences
- Life prediction accuracy

### Signal Processing Testing

**FFT Testing:**
- Algorithm correctness (compare with numpy)
- Frequency resolution
- Nyquist theorem compliance
- Inverse FFT accuracy
- Power conservation

**Filtering Testing:**
- Filter coefficient validation
- Frequency response verification
- Phase shift testing
- Boundary effect handling

**Spectral Testing:**
- PSD calculation accuracy
- Frequency resolution effects
- Window function impact
- Spectral moment calculations

**Rainflow Testing:**
- ASTM E1049-85 compliance
- Cycle extraction accuracy
- Peak-valley detection
- Stress range validation

---

## Migration Path from Existing Solvers

### Backward Compatibility Strategy

**Goal:** No breaking changes for existing code during migration

**Approach:**
1. Create new `base_solvers` module in parallel
2. Keep existing solver implementations
3. Update existing solvers to inherit from `BaseSolver`
4. Create adapter layer for legacy code
5. Deprecate old imports over 2-3 months

**Example Migration:**
```python
# Old code (continue to work)
from digitalmodel.marine.catenary import CatenatyRiser
solver = CatenatyRiser()

# New code (use base_solvers)
from digitalmodel.base_solvers.marine import CatenaaryRiser
solver = CatenaaryRiser(config_path="config/marine/catenary.yaml")

# Adapter for legacy code (behind the scenes)
class CatenaaryRiser(BaseConfigurableSolver):
    """New implementation of catenary solver."""
    pass

# Re-export from old location for compatibility
digitalmodel.marine.CatenaaryRiser = CatenaaryRiser
```

### Consolidation Steps per Solver

For each existing solver:
1. Copy implementation to `base_solvers/[domain]/[solver].py`
2. Create wrapper inheriting from `BaseSolver`/`ConfigurableSolver`
3. Implement `validate_inputs()`, `solve()`, `get_solver_metadata()`
4. Create YAML configuration file in `config/[domain]/`
5. Write 8-10 comprehensive tests
6. Update imports in legacy code to use new location
7. Mark old location as deprecated

---

## Performance Benchmarks

### Solver Performance Targets

| Solver | Operation | Target | Notes |
|--------|-----------|--------|-------|
| **Catenary** | Full analysis | < 100ms | 1000-point shape |
| **Hydrodynamic** | Coefficient calc | < 50ms | Single frequency |
| **Environmental** | Load computation | < 30ms | Full water column |
| **Wave Spectrum** | Spectrum generation | < 20ms | 1000 frequency points |
| **Von Mises** | Stress calc | < 5ms | Per element |
| **Buckling** | Load calculation | < 10ms | Single mode |
| **FFT** | 1024-point FFT | < 20ms | Full transformation |
| **Filtering** | Signal filter | < 50ms | 10k samples |
| **S-N Curves** | Lookup/interpolate | < 5ms | Single point |
| **Damage** | Cumulative calc | < 30ms | 1000 cycles |

### Memory Benchmarks

| Solver | Input Size | Memory | Notes |
|--------|-----------|--------|-------|
| Catenary | 1000 points | < 5MB | Full state |
| Hydrodynamic | 100 frequencies | < 2MB | Matrix storage |
| FFT | 100k samples | < 20MB | Complex array |
| S-N Curves | All 221 curves | < 50MB | In-memory database |

---

## Configuration Validation

### Runtime Validation

All configurations validated at load time:

```python
class SolverConfig(BaseModel):
    """Base configuration model for validation."""

    class Config:
        extra = "forbid"  # No extra fields allowed
        validate_assignment = True

    # Pydantic handles:
    # - Type checking
    # - Range validation (minimum, maximum)
    # - Required field verification
    # - Custom validators
    # - Unit conversion if needed
```

### Configuration Error Handling

```python
try:
    solver = CatenaaryRiser(config_path="config/marine/catenary.yaml")
except SolverConfigError as e:
    # Handle configuration errors
    print(f"Configuration invalid: {e}")
except FileNotFoundError:
    # Handle missing config file
    print(f"Config file not found")
```

---

## Documentation Index

- **Solver Development Guide:** SOLVER_DEVELOPMENT_GUIDE.md
- **Configuration Schema:** CONFIGURATION_GUIDE.md
- **API Reference:** API_REFERENCE.md
- **Migration Guide:** MIGRATION_GUIDE.md
- **Integration Examples:** INTEGRATION_EXAMPLES.md

---

**Next:** See SOLVER_DEVELOPMENT_GUIDE.md for templates and examples for implementing new solvers.
