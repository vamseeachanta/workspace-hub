---
name: orcaflex-environment-config
description: Configure OrcaFlex environmental conditions including wave spectra (JONSWAP,
  Dean Stream), current profiles, wind loading, and seabed properties for offshore
  analysis.
type: reference
version: 1.0.0
updated: 2026-01-17
category: engineering
triggers:
- environment setup
- wave configuration
- current profile
- wind setup
- JONSWAP spectrum
- sea state
- environmental loading
- seabed properties
capabilities: []
requires: []
tags: []
scripts_exempt: true
---

# Orcaflex Environment Config

## When to Use

- Setting up wave conditions for simulations
- Configuring depth-varying current profiles
- Adding wind loads to vessel/structure analysis
- Defining seabed properties for touchdown regions
- Creating consistent environmental load cases
- Multi-directional wave/current combinations

## Python API

### Basic Environment Setup

```python
from digitalmodel.solvers.fea_model.environment_components import Environment

def setup_environment(config: dict) -> dict:
    """
    Configure OrcaFlex environment from config.

    Args:
        config: Environment configuration dictionary


*See sub-skills for full details.*
### Direct OrcFxAPI Configuration

```python
import OrcFxAPI

def configure_orcaflex_environment(
    model: OrcFxAPI.Model,
    config: dict
) -> OrcFxAPI.OrcaFlexObject:
    """
    Configure environment directly in OrcFxAPI.


*See sub-skills for full details.*
### Current Profile Configuration

```python
import OrcFxAPI

def set_current_profile(
    model: OrcFxAPI.Model,
    surface_speed: float,
    direction: float,
    depth_factors: list
) -> None:
    """

*See sub-skills for full details.*
### Wind Configuration

```python
import OrcFxAPI

def configure_wind(
    model: OrcFxAPI.Model,
    speed: float,
    direction: float,
    reference_height: float = 10.0,
    apply_to_vessels: bool = True,
    apply_to_lines: bool = False,

*See sub-skills for full details.*
### JONSWAP Gamma Calculation

```python
import math

def calculate_jonswap_gamma(Hs: float, Tp: float) -> float:
    """
    Calculate JONSWAP gamma from Hs and Tp.

    Uses DNV-RP-C205 relationship.

    Args:

*See sub-skills for full details.*
### Multi-Directional Waves

```python
import OrcFxAPI

def configure_multi_directional_waves(
    model: OrcFxAPI.Model,
    wave_components: list
) -> None:
    """
    Configure multi-directional wave system.


*See sub-skills for full details.*

## Related Skills

- [orcaflex-modeling](../orcaflex-modeling/SKILL.md) - Run OrcaFlex simulations
- [orcaflex-operability](../orcaflex-operability/SKILL.md) - Multi-sea-state analysis
- [hydrodynamics](../hydrodynamics/SKILL.md) - Wave spectra management
- [mooring-design](../mooring-design/SKILL.md) - Environmental loading

## References

- DNV-RP-C205: Environmental Conditions and Loads
- API RP 2MET: Metocean
- OrcaFlex: Environment Data
- Source: `src/digitalmodel/modules/fea_model/environment_components.py`

## Sub-Skills

- [Complete Environment Configuration (+1)](complete-environment-configuration/SKILL.md)
- [Wave Configuration (+2)](wave-configuration/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [[1.0.0] - 2026-01-17](100-2026-01-17/SKILL.md)
- [Wave Types (+2)](wave-types/SKILL.md)
- [Environment YAML Output](environment-yaml-output/SKILL.md)
- [Common Errors and Fixes (+2)](common-errors-and-fixes/SKILL.md)
- [Environment Sanity Checks (+1)](environment-sanity-checks/SKILL.md)
