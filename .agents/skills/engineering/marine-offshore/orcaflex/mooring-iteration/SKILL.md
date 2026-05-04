---
name: orcaflex-mooring-iteration
description: Iterate mooring line lengths to achieve target pretensions using scipy
  optimization, Newton-Raphson, or EA-based methods. Use for mooring system design,
  pretension optimization, and CALM/SALM buoy configuration.
type: reference
version: 1.0.0
updated: 2026-01-17
category: engineering
triggers:
- mooring tension iteration
- pretension optimization
- line length adjustment
- mooring design
- target tension
- tension matching
- mooring optimization
- CALM mooring
- SALM mooring
capabilities: []
requires: []
tags: []
scripts_exempt: true
---

# Orcaflex Mooring Iteration

## When to Use

- Achieving target mooring line pretensions
- Optimizing line lengths for design loads
- CALM/SALM buoy mooring configuration
- Spread mooring system design
- Turret mooring optimization
- Multi-line tension balancing
- Mooring system verification

## Prerequisites

- OrcaFlex license (for simulation)
- Python environment with `digitalmodel` package installed
- Initial mooring model (close to target configuration)
- Target pretensions for each line

## Python API

### Basic Usage

```python
from digitalmodel.orcaflex.mooring_tension_iteration import (
    MooringTensionIterator,
    IterationConfig,
    LineConfig,
    ConvergenceConfig
)

# Define configuration
config = IterationConfig(

*See sub-skills for full details.*
### With Vessel Fixing

```python
from digitalmodel.orcaflex.mooring_tension_iteration import (
    MooringTensionIterator,
    IterationConfig,
    VesselConfig
)

config = IterationConfig(
    method="scipy",
    vessel_config=VesselConfig(

*See sub-skills for full details.*
### Convergence Monitoring

```python
# After iteration
result = iterator.iterate_to_targets()

# Access convergence history
for i, error in enumerate(result.convergence_history):
    print(f"Iteration {i+1}: Max error = {error:.2f}%")

# Plot convergence
import matplotlib.pyplot as plt

*See sub-skills for full details.*
### Generate Report

```python
# Generate comprehensive report
report = iterator.generate_report(output_path="iteration_report.txt")
print(report)

# Report includes:
# - Configuration summary
# - Target vs achieved tensions
# - Length modifications
# - Convergence history
```

## Related Skills

- [orcaflex-modeling](../orcaflex-modeling/SKILL.md) - Run OrcaFlex simulations
- [mooring-design](../mooring-design/SKILL.md) - Design mooring systems
- [orcaflex-line-wizard](../orcaflex-line-wizard/SKILL.md) - Configure line properties
- [catenary-riser](../catenary-riser/SKILL.md) - Catenary analysis

## References

- OrcaFlex Line Setup Wizard: Orcina Documentation
- API RP 2SK: Design and Analysis of Stationkeeping Systems
- DNV-OS-E301: Position Mooring
- Source: `src/digitalmodel/modules/orcaflex/mooring_tension_iteration/`
- Tests: `tests/modules/orcaflex/mooring-tension-iteration/`

## Sub-Skills

- [Basic Configuration (+1)](basic-configuration/SKILL.md)
- [Initial Model (+2)](initial-model/SKILL.md)

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [[1.0.0] - 2026-01-17](100-2026-01-17/SKILL.md)
- [1. Scipy Optimization (Recommended) (+2)](1-scipy-optimization-recommended/SKILL.md)
- [Scipy Method (+2)](scipy-method/SKILL.md)
- [Iteration Result (+1)](iteration-result/SKILL.md)
- [With Mooring Design (+1)](with-mooring-design/SKILL.md)
