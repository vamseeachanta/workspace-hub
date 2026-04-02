---
name: orcaflex-vessel-setup
description: Configure 6-DOF vessels in OrcaFlex with hydrodynamic properties, RAO
  import from AQWA, and vessel type creation. Covers initial position, orientation,
  calculation settings, and motion options.
type: reference
version: 1.0.0
updated: 2026-01-17
category: engineering
triggers:
- vessel setup
- create vessel
- vessel configuration
- 6-DOF vessel
- vessel type
- vessel properties
- vessel initialization
- AQWA vessel import
capabilities: []
requires: []
tags: []
scripts_exempt: true
---

# Orcaflex Vessel Setup

## When to Use

- Creating new vessels in OrcaFlex models
- Configuring 6-DOF motion properties
- Importing vessel hydrodynamics from AQWA
- Setting up vessel calculation options
- Defining vessel types with RAO data
- Configuring drift, damping, and wave loads

## Python API

### Basic Vessel Creation

```python
from digitalmodel.solvers.fea_model.Vessel_components import Vessel
from digitalmodel.solvers.fea_model.VesselType_components import VesselType

def create_vessel(config: dict) -> dict:
    """
    Create OrcaFlex vessel configuration.

    Args:
        config: Vessel configuration dictionary

*See sub-skills for full details.*
### AQWA Vessel Import

```python
from digitalmodel.solvers.fea_model.preprocess.load_vessel import LoadVessel
import OrcFxAPI

def import_vessel_from_aqwa(
    model: OrcFxAPI.Model,
    aqwa_file: str,
    vessel_name: str,
    import_config: dict = None
) -> OrcFxAPI.OrcaFlexObject:

*See sub-skills for full details.*
### Vessel Calculation Settings

```python
import OrcFxAPI

def configure_vessel_calculations(
    vessel: OrcFxAPI.OrcaFlexObject,
    settings: dict
) -> None:
    """
    Configure vessel calculation options.


*See sub-skills for full details.*
### Multi-Body Import

```python
import OrcFxAPI

def import_multi_body_system(
    model: OrcFxAPI.Model,
    aqwa_file: str,
    body_mapping: list
) -> dict:
    """
    Import multi-body system from AQWA.

*See sub-skills for full details.*

## Related Skills

- [orcaflex-modeling](../orcaflex-modeling/SKILL.md) - Run OrcaFlex simulations
- [orcaflex-rao-import](../orcaflex-rao-import/SKILL.md) - RAO data import
- [aqwa-analysis](../aqwa-analysis/SKILL.md) - AQWA analysis
- [hydrodynamics](../hydrodynamics/SKILL.md) - Hydrodynamic coefficients

## References

- OrcaFlex: Vessel Type Data
- OrcaFlex: Importing Hydrodynamic Data
- ANSYS AQWA: Output File Format
- Source: `src/digitalmodel/modules/fea_model/Vessel_components.py`
- Source: `src/digitalmodel/modules/fea_model/VesselType_components.py`
- Source: `src/digitalmodel/modules/fea_model/preprocess/load_vessel.py`

## Sub-Skills

- [Basic Vessel Configuration (+1)](basic-vessel-configuration/SKILL.md)
- [Data Import (+2)](data-import/SKILL.md)

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [[1.0.0] - 2026-01-17](100-2026-01-17/SKILL.md)
- [Vessel Object (+1)](vessel-object/SKILL.md)
- [Vessel Properties YAML](vessel-properties-yaml/SKILL.md)
- [1. FPSO with AQWA Hydrodynamics (+2)](1-fpso-with-aqwa-hydrodynamics/SKILL.md)
