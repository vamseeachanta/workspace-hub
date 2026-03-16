---
name: orcawave-to-orcaflex
description: Integration specialist for converting OrcaWave diffraction results to
  OrcaFlex vessel types. Handles hydrodynamic database generation, RAO import, viscous
  damping addition, and coordinate system transformations.
version: 1.0.0
updated: 2026-01-17
category: engineering
triggers:
- OrcaWave to OrcaFlex
- hydrodynamic database
- vessel type creation
- RAO import
- diffraction to time domain
- added mass damping export
- OrcaFlex vessel setup
capabilities: []
requires: []
see_also:
- orcawave-to-orcaflex-version-metadata
- orcawave-to-orcaflex-workflow-overview
- orcawave-to-orcaflex-standard-export-configuration
- orcawave-to-orcaflex-supported-output-formats
- orcawave-to-orcaflex-cli-usage
- orcawave-to-orcaflex-pre-export-validation
- orcawave-to-orcaflex-generated-yaml-structure
tags: []
scripts_exempt: true
---

# Orcawave To Orcaflex

## When to Use

- Converting OrcaWave results (.owr) to OrcaFlex vessel type
- Creating hydrodynamic database for time-domain analysis
- Importing RAO data from diffraction analysis
- Adding viscous damping to radiation damping
- Transforming coordinate systems between tools
- Setting up vessel types with full hydrodynamic properties
- Batch conversion of multiple loading conditions

## Python API

### Basic Conversion

```python
from digitalmodel.diffraction.orcawave_converter import OrcaWaveConverter
from digitalmodel.diffraction.orcaflex_exporter import OrcaFlexExporter

# Load OrcaWave results
import OrcFxAPI

# Option 1: From OrcaWave model directly
orcawave_model = OrcFxAPI.DiffractionModel("models/fpso.owr")
vessel = orcawave_model.Vessel

*See sub-skills for full details.*
### With Viscous Damping

```python
from digitalmodel.orcawave.orcaflex_export import OrcaWaveToOrcaFlex

# Initialize converter with damping options
converter = OrcaWaveToOrcaFlex()

# Load OrcaWave results
converter.load_orcawave("models/fpso.owr")

# Add viscous damping (percentage of critical)

*See sub-skills for full details.*
### Full Hydrodynamic Database

```python
from digitalmodel.orcawave.orcaflex_export import HydrodynamicDatabaseCreator

# Create complete hydrodynamic database
db_creator = HydrodynamicDatabaseCreator()

# Load all loading conditions
db_creator.add_condition(
    name="full_load",
    orcawave_file="models/fpso_full.owr",

*See sub-skills for full details.*
### RAO Import with Validation

```python
from digitalmodel.orcawave.rao_import import RAOImporter
from digitalmodel.diffraction.output_validator import OutputValidator

# Import RAOs with validation
importer = RAOImporter()

# Load OrcaWave RAOs
raos = importer.load_from_orcawave("models/fpso.owr")


*See sub-skills for full details.*
### Coordinate Transformation

```python
from digitalmodel.orcawave.coordinate_transform import CoordinateTransformer

# Handle coordinate system differences
transformer = CoordinateTransformer()

# OrcaWave uses different conventions than OrcaFlex
# Transform origin location
transformer.set_orcawave_origin(
    x=150.0,  # Midship

*See sub-skills for full details.*

## Related Skills

- [orcawave-analysis](../orcawave-analysis/SKILL.md) - OrcaWave diffraction analysis
- [orcaflex-vessel-setup](../orcaflex-vessel-setup/SKILL.md) - OrcaFlex vessel configuration
- [orcaflex-rao-import](../orcaflex-rao-import/SKILL.md) - RAO data import
- [hydrodynamics](../hydrodynamics/SKILL.md) - Coefficient management

## References

- OrcaWave Data Format Specification
- OrcaFlex Vessel Type Documentation
- Converter Implementation: `src/digitalmodel/modules/diffraction/orcawave_converter.py`
- Exporter Implementation: `src/digitalmodel/modules/diffraction/orcaflex_exporter.py`

---

**Version History**

- **1.0.0** (2026-01-17): Initial release with conversion, validation, and multi-format export

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [Workflow Overview](workflow-overview/SKILL.md)
- [Standard Export Configuration (+1)](standard-export-configuration/SKILL.md)
- [Supported Output Formats (+1)](supported-output-formats/SKILL.md)
- [CLI Usage](cli-usage/SKILL.md)
- [Pre-Export Validation](pre-export-validation/SKILL.md)
- [Generated YAML Structure](generated-yaml-structure/SKILL.md)
