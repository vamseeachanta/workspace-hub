---
name: orcaflex-line-wizard
description: Configure OrcaFlex line properties and use the Line Setup Wizard for
  automatic tension/length calculations. Use for mooring line configuration, riser
  setup, and achieving target line properties.
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
see_also:
- orcaflex-line-wizard-version-metadata
- orcaflex-line-wizard-100-2026-01-17
- orcaflex-line-wizard-calculation-modes
- orcaflex-line-wizard-yaml-based-line-setup
- orcaflex-line-wizard-common-line-setup-properties
- orcaflex-line-wizard-with-mooring-iteration
- orcaflex-line-wizard-common-errors-and-fixes
- orcaflex-line-wizard-post-wizard-checks
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

- [orcaflex-modeling](../orcaflex-modeling/SKILL.md) - Run OrcaFlex simulations
- [orcaflex-mooring-iteration](../orcaflex-mooring-iteration/SKILL.md) - Advanced tension iteration
- [mooring-design](../mooring-design/SKILL.md) - Design mooring systems
- [orcaflex-static-debug](../orcaflex-static-debug/SKILL.md) - Troubleshoot convergence

## References

- OrcaFlex Help: Line Setup Wizard
- OrcFxAPI Documentation: Model.InvokeLineSetupWizard()
- Source: `src/digitalmodel/modules/orcaflex/orcaflex_model_linesetup_wizard.py`

## Sub-Skills

- [Before Using Line Setup Wizard (+2)](before-using-line-setup-wizard/SKILL.md)

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [[1.0.0] - 2026-01-17](100-2026-01-17/SKILL.md)
- [Calculation Modes](calculation-modes/SKILL.md)
- [YAML-Based Line Setup (+1)](yaml-based-line-setup/SKILL.md)
- [Common Line Setup Properties (+1)](common-line-setup-properties/SKILL.md)
- [With Mooring Iteration (+1)](with-mooring-iteration/SKILL.md)
- [Common Errors and Fixes (+1)](common-errors-and-fixes/SKILL.md)
- [Post-Wizard Checks](post-wizard-checks/SKILL.md)
