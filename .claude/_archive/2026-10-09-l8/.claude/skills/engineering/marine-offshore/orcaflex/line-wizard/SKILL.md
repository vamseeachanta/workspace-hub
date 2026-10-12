---
name: orcaflex-line-wizard
description: Configure OrcaFlex line properties and use the Line Setup Wizard for
  automatic tension/length calculations. Use for mooring line configuration, riser
  setup, and achieving target line properties.
type: reference
version: 1.0.0
updated: 2026-01-17
category: engineering
triggers:
- line setup wizard
- line configuration
- target tension
- line length calculation
- mooring line setup
- riser configuration
- line properties
- segment configuration
capabilities: []
requires: []
tags: []
scripts_exempt: true
---

# Orcaflex Line Wizard

## When to Use

- Setting up mooring lines with target pretensions
- Configuring riser lines with specified top tensions
- Calculating line lengths for given tension targets
- Calculating tensions for given line lengths
- Multi-line mooring system configuration
- Initial model setup before detailed analysis

## Python API

### Basic Line Setup

```python
import OrcFxAPI

# Load model
model = OrcFxAPI.Model("mooring_model.dat")

# Configure Line Setup Wizard
model.general.LineSetupCalculationMode = "Calculate line lengths"
model.general.LineSetupMaxDamping = 20  # For numerical stability


*See sub-skills for full details.*
### Comprehensive Line Configuration

```python
import OrcFxAPI
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class LineSetupConfig:
    """Configuration for a line in the setup wizard."""
    name: str
    target_variable: str = "Tension"  # "Tension" or "Length"

*See sub-skills for full details.*
### Line Section Configuration

```python
def configure_line_sections(
    model: OrcFxAPI.Model,
    line_name: str,
    sections: list
) -> None:
    """
    Configure line sections with multiple line types.

    Args:

*See sub-skills for full details.*

## Related Skills

- orcaflex-modeling - Run OrcaFlex simulations
- orcaflex-mooring-iteration - Advanced tension iteration
- mooring-design - Design mooring systems
- orcaflex-static-debug - Troubleshoot convergence

## References

- OrcaFlex Help: Line Setup Wizard
- OrcFxAPI Documentation: Model.InvokeLineSetupWizard()
- Source: `src/digitalmodel/solvers/orcaflex/orcaflex_model_linesetup_wizard.py`

## Sub-Skills

- Before Using Line Setup Wizard (+2)

## Sub-Skills

- Error Handling

## Sub-Skills

- Version Metadata
- [[1.0.0] - 2026-01-17](100-2026-01-17/SKILL.md)
- Calculation Modes
- YAML-Based Line Setup (+1)
- Common Line Setup Properties (+1)
- With Mooring Iteration (+1)
- Common Errors and Fixes (+1)
- Post-Wizard Checks
