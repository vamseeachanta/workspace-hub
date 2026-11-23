# Phase 2.2 Mathematical Solvers Consolidation Specification

> Spec: phase2-task2-2
> Created: 2025-01-09
> Status: Planning
> Domain: digitalmodel - Core Infrastructure
> Dependencies: Phase 2.1 Configuration Framework (ConfigManager, ConfigModel)

## Overview

Consolidate 30+ existing mathematical solver modules across 10+ domains (marine engineering, structural analysis, fatigue analysis, signal processing, specialized domains) into a unified `base_solvers` architecture within the digitalmodel core infrastructure.

The unified interface will enable developers to implement new solvers by inheriting from `BaseSolver` or domain-specific abstractions, while maintaining backward compatibility with existing solver implementations. This consolidation establishes the foundation for solver discovery, configuration management, and comprehensive testing across all domains.

## User Stories

### Story 1: Consistent Solver Interface

**As a developer**, I want to use solvers through a consistent interface so I can learn once and use everywhere.

**Workflow:**
1. Import any solver from digitalmodel.base_solvers
2. Pass configuration and inputs
3. Call solve() method
4. Receive validated outputs
5. Access solver metadata and capabilities

**Acceptance Criteria:**
- All solvers follow identical interface (validate_inputs, solve, get_solver_metadata)
- Configuration loaded via ConfigManager (Phase 2.1)
- Error handling consistent across domains
- Solver discovery via registry pattern

### Story 2: Easy Solver Implementation

**As a domain expert**, I want to implement new solvers easily by inheriting from BaseSolver so I can focus on algorithms.

**Workflow:**
1. Create new solver class inheriting from ConfigurableSolver
2. Define YAML configuration schema
3. Implement validate_inputs() and solve() methods
4. Register solver in domain module
5. Write TDD tests

**Acceptance Criteria:**
- Solver boilerplate < 50 lines
- Configuration auto-validated via schema
- Error handling inherited and consistent
- Template examples for each domain

### Story 3: Comprehensive Solver Testing

**As a test engineer**, I want comprehensive solver tests so I can ensure quality across domains.

**Workflow:**
1. Run unified test suite covering all solvers
2. See domain-specific test details
3. Verify 90%+ coverage across all solvers
4. Access fixture data for each solver
5. Benchmark performance

**Acceptance Criteria:**
- 40+ unit tests covering all solvers
- 90%+ code coverage across base_solvers
- Domain-specific test suites (10+ tests each)
- Test fixtures for sample data
- Performance benchmarks

## Spec Scope

### 1. Base Solver Architecture

**Components:**
- Abstract base classes (BaseSolver, ConfigurableSolver, AnalysisSolver)
- Solver protocols and interfaces
- Configuration management integration
- Error handling hierarchy
- Solver registry system

**Details:**
- BaseSolver: Core interface for all solvers
- ConfigurableSolver: Adds YAML config management
- AnalysisSolver: Specialized for domain analysis (stress, fatigue, wave, etc.)
- SolverRegistry: Dynamic solver discovery and registration
- SolverError hierarchy: Domain-specific exceptions

### 2. Marine Engineering Solvers

**Consolidate:**
- Catenary riser analysis (shape, tension, forces)
- Hydrodynamic coefficients (added mass, damping, drag)
- Environmental loading (waves, currents, wind)
- Wave spectrum modeling (JONSWAP, Pierson-Moskowitz)
- Ocean loading calculation (OCIMF patterns)

**Unified under:** `digitalmodel.base_solvers.marine`

**Test Coverage:** 8-10 tests per solver, 90%+ coverage

### 3. Structural & Fatigue Solvers

**Consolidate:**
- Von Mises stress calculation (multiaxial stress states)
- Buckling analysis (Euler, reduced modulus, Johnson)
- Damage accumulation (Miner's rule, non-linear)
- S-N curves (221 curves from 17 international standards: DNV, API, BS, ABS, etc.)

**Unified under:** `digitalmodel.base_solvers.structural`, `digitalmodel.base_solvers.fatigue`

**Test Coverage:** 8-10 tests per solver, 90%+ coverage

### 4. Signal Processing Solvers

**Consolidate:**
- FFT (Fast Fourier Transform)
- Inverse FFT
- Digital filtering (low-pass, high-pass, band-pass)
- Spectral analysis (power spectral density, frequency response)
- Rainflow cycle counting (ASTM E1049-85)
- Fatigue cycle integration

**Unified under:** `digitalmodel.base_solvers.signal`

**Test Coverage:** 8-10 tests per solver, 90%+ coverage

### 5. Specialized Domain Solvers

**Consolidate:**
- Mooring system design (CALM/SALM, catenary, spread mooring)
- OrcaFlex model post-processing
- Vortex-Induced Vibration (VIV) analysis
- Response Amplitude Operator (RAO) analysis
- API compliance checking

**Unified under:** `digitalmodel.base_solvers.specialized`

**Test Coverage:** 8-10 tests per solver, 90%+ coverage

### 6. Configuration Integration

**Consolidate with Phase 2.1:**
- YAML configuration files per solver
- Configuration schema validation
- ConfigManager integration
- Runtime configuration loading
- Configuration inheritance patterns

**Pattern:**
```yaml
# config/marine/catenary.yaml
solver:
  name: catenary_riser
  version: "1.0"
  domain: marine

parameters:
  material_properties:
    outer_diameter: 0.5  # meters
    wall_thickness: 0.02
    steel_density: 7850  # kg/m³

  environmental:
    water_depth: 1000  # meters
    wave_height: 2.5
    current_velocity: 1.2
```

### 7. Testing Infrastructure

**Create comprehensive test suite:**
- Unit tests for validate_inputs() (data validation, constraints)
- Integration tests for solve() (algorithm correctness)
- Domain-specific tests (8-10 per solver)
- Test fixtures with realistic data
- Benchmark performance tests
- Error handling verification

**Target:** 40+ total tests, 90%+ code coverage

### 8. Documentation & Guidance

**Create:**
- Solver development guide with templates
- API documentation for each solver
- Configuration schema documentation
- Domain-specific examples
- Migration guide from old to new patterns

## Out of Scope

- **Database Integration:** ORM/model storage handled by Phase 2.1 ConfigModel
- **Real-Time Monitoring:** Solver execution monitoring/dashboards (future phase)
- **Distributed Computing:** Multi-process/cluster execution (future enhancement)
- **Solver Optimization:** Algorithm optimization or parallelization (domain-specific)
- **Visualization:** Result visualization (separate module)
- **External Service Integration:** API calls to external solvers
- **Version Management:** Solver versioning beyond registry

## Expected Deliverables

### 1. Code Structure
```
digitalmodel/src/digitalmodel/base_solvers/
├── __init__.py
├── base.py                      # BaseSolver, ConfigurableSolver, AnalysisSolver
├── interfaces.py                # Protocols and abstract interfaces
├── registry.py                  # SolverRegistry, solver discovery
├── exceptions.py                # SolverError hierarchy
├── config/
│   ├── __init__.py
│   ├── solver_config.py         # SolverConfig, ConfigSchema
│   └── schemas.py               # Pydantic schemas for validation
├── marine/
│   ├── __init__.py
│   ├── catenary.py              # Catenary riser solver
│   ├── hydrodynamic.py          # Hydrodynamic coefficients
│   ├── environmental.py         # Environmental loading
│   └── wave_spectra.py          # Wave spectrum models
├── structural/
│   ├── __init__.py
│   ├── stress.py                # Von Mises stress
│   ├── buckling.py              # Buckling analysis
│   └── multiaxial.py            # Multiaxial stress states
├── fatigue/
│   ├── __init__.py
│   ├── damage.py                # Damage accumulation
│   ├── sn_curves.py             # S-N curve management (221 curves)
│   └── integration.py           # Cycle integration
├── signal/
│   ├── __init__.py
│   ├── fft.py                   # FFT/IFFT
│   ├── filtering.py             # Digital filtering
│   ├── spectral.py              # Spectral analysis
│   └── rainflow.py              # Rainflow cycle counting
├── specialized/
│   ├── __init__.py
│   ├── mooring.py               # Mooring system design
│   ├── orcaflex.py              # OrcaFlex post-processing
│   ├── viv.py                   # VIV analysis
│   ├── rao.py                   # RAO analysis
│   └── api_compliance.py        # API standards checking
└── utils/
    ├── __init__.py
    ├── validators.py            # Input validation utilities
    └── converters.py            # Unit conversion utilities
```

### 2. Configuration Files
```
digitalmodel/config/solvers/
├── marine/
│   ├── catenary.yaml
│   ├── hydrodynamic.yaml
│   ├── environmental.yaml
│   └── wave_spectra.yaml
├── structural/
│   ├── stress.yaml
│   ├── buckling.yaml
│   └── multiaxial.yaml
├── fatigue/
│   ├── damage.yaml
│   ├── sn_curves.yaml
│   └── integration.yaml
├── signal/
│   ├── fft.yaml
│   ├── filtering.yaml
│   ├── spectral.yaml
│   └── rainflow.yaml
└── specialized/
    ├── mooring.yaml
    ├── orcaflex.yaml
    ├── viv.yaml
    ├── rao.yaml
    └── api_compliance.yaml
```

### 3. Test Suite
```
digitalmodel/tests/unit/base_solvers/
├── __init__.py
├── test_base.py                 # BaseSolver, interfaces (12+ tests)
├── test_config.py               # Configuration management (8+ tests)
├── test_registry.py             # SolverRegistry (6+ tests)
├── marine/
│   ├── test_catenary.py         # 10+ tests
│   ├── test_hydrodynamic.py     # 10+ tests
│   ├── test_environmental.py    # 8+ tests
│   └── test_wave_spectra.py     # 8+ tests
├── structural/
│   ├── test_stress.py           # 10+ tests
│   ├── test_buckling.py         # 10+ tests
│   └── test_multiaxial.py       # 8+ tests
├── fatigue/
│   ├── test_damage.py           # 10+ tests
│   ├── test_sn_curves.py        # 12+ tests (221 curves)
│   └── test_integration.py      # 8+ tests
├── signal/
│   ├── test_fft.py              # 10+ tests
│   ├── test_filtering.py        # 10+ tests
│   ├── test_spectral.py         # 8+ tests
│   └── test_rainflow.py         # 10+ tests
└── specialized/
    ├── test_mooring.py          # 10+ tests
    ├── test_orcaflex.py         # 8+ tests
    ├── test_viv.py              # 8+ tests
    ├── test_rao.py              # 8+ tests
    └── test_api_compliance.py   # 6+ tests

digitalmodel/tests/fixtures/
├── marine/
│   ├── catenary_sample.json
│   ├── hydrodynamic_data.csv
│   └── wave_spectrum_data.csv
├── structural/
│   ├── stress_cases.json
│   └── buckling_parameters.json
└── ...
```

### 4. Documentation
- `SOLVER_DEVELOPMENT_GUIDE.md` - Template and patterns for implementing solvers
- `API_REFERENCE.md` - Complete API documentation
- `MIGRATION_GUIDE.md` - Instructions for migrating existing solvers
- `CONFIGURATION_GUIDE.md` - Detailed configuration schema documentation
- Inline code documentation with docstrings

### 5. Test Coverage Report
- 90%+ overall code coverage
- Per-solver coverage metrics
- Branch coverage for critical algorithms
- Performance benchmarks for each solver

## Spec Documentation

### Related Specs
- **Phase 2.1 Configuration Framework:** @.agent-os/specs/phase2-task2-1/spec.md
- **Digital Model Core:** @.agent-os/product/mission.md

### Solver References
- **Marine Analysis Skill:** @~/.claude/skills/marine-analysis/SKILL.md
- **Fatigue Analysis Skill:** @~/.claude/skills/fatigue-analysis/SKILL.md
- **Signal Analysis Skill:** @~/.claude/skills/signal-analysis/SKILL.md

### Standards
- **Code Style:** @~/.agent-os/standards/code-style.md
- **Testing Framework:** @docs/modules/standards/TESTING_FRAMEWORK_STANDARDS.md
- **File Organization:** @docs/modules/standards/FILE_ORGANIZATION_STANDARDS.md

### Workflow & Methodology
- **TDD Development:** @docs/modules/workflow/DEVELOPMENT_WORKFLOW.md
- **SPARC Methodology:** @~/.agent-os/instructions/execute-tasks.md
- **AI Agent Guidelines:** @docs/modules/ai/AI_AGENT_GUIDELINES.md

## Implementation Resources

### Phase 2.1 Dependencies
- ConfigManager class (configuration loading/validation)
- ConfigModel base class (configuration data models)
- Solver configuration schema patterns

### External Standards
- DNV standards for marine/structural analysis
- API standards for oil & gas compliance
- ASTM E1049-85 for rainflow cycle counting
- International S-N curve databases

### Existing Modules to Consolidate
- digitalmodel.marine.catenary (existing catenary solver)
- digitalmodel.marine.hydrodynamic (existing hydrodynamic solver)
- digitalmodel.structural.stress (existing stress calculation)
- digitalmodel.fatigue.damage (existing damage accumulation)
- digitalmodel.signal.fft (existing FFT solver)
- digitalmodel.specialized.mooring (existing mooring design)
- digitalmodel.specialized.orcaflex (existing OrcaFlex interface)
- digitalmodel.specialized.viv (existing VIV analysis)
- Additional domain-specific solvers across portfolio

## Success Criteria

### Code Quality
- ✅ 90%+ test coverage across all solvers
- ✅ All solvers follow consistent interface pattern
- ✅ Zero breaking changes for existing solver usage
- ✅ All code follows style guide (@~/.agent-os/standards/code-style.md)
- ✅ Type hints on all public methods

### Functionality
- ✅ All 30+ solvers migrated to base_solvers structure
- ✅ Configuration management via Phase 2.1 ConfigManager
- ✅ Error handling consistent across domains
- ✅ Solver discovery via registry pattern
- ✅ All tests passing

### Documentation
- ✅ Complete solver development guide with templates
- ✅ Migration guide for existing solvers
- ✅ API documentation complete
- ✅ Configuration schema documented
- ✅ Examples for each solver domain

### Testing
- ✅ 40+ unit/integration tests
- ✅ Test fixtures for all solvers
- ✅ Performance benchmarks recorded
- ✅ Error handling verified
- ✅ Backward compatibility confirmed

---

## Spec Documentation

- **Consolidation Strategy:** @.agent-os/specs/phase2-task2-2/sub-specs/consolidation-strategy.md
- **Solver Development Guide:** @.agent-os/specs/phase2-task2-2/sub-specs/solver-development-guide.md
- **Tasks Breakdown:** @.agent-os/specs/phase2-task2-2/tasks.md
