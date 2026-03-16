---
name: orcaflex-rao-import
description: Import RAO (Response Amplitude Operator) data from external sources including
  AQWA, OrcaFlex, and CSV files. Includes validation, interpolation, and conversion
  for OrcaFlex vessel type creation.
version: 1.0.0
updated: 2026-01-17
category: engineering
triggers:
- RAO import
- import vessel RAOs
- AQWA to OrcaFlex
- RAO conversion
- vessel hydrodynamics
- transfer functions
- motion RAOs
- RAO interpolation
capabilities: []
requires: []
see_also:
- orcaflex-rao-import-version-metadata
- orcaflex-rao-import-100-2026-01-17
- orcaflex-rao-import-supported-formats
- orcaflex-rao-import-6-dof-motion-raos
- orcaflex-rao-import-orcaflex-yaml-format
- orcaflex-rao-import-aqwa-import
tags: []
scripts_exempt: true
---

# Orcaflex Rao Import

## When to Use

- Import RAOs from ANSYS AQWA analysis
- Extract RAOs from existing OrcaFlex models
- Import RAOs from experimental data (CSV/Excel)
- Validate RAO data quality
- Interpolate RAOs to new frequency/heading grids
- Create OrcaFlex vessel types with imported RAOs

## Python API

### Basic RAO Import

```python
from digitalmodel.marine_ops.marine_analysis.rao_processor import RAOProcessor

# Initialize processor
processor = RAOProcessor()

# Import from AQWA
rao_data = processor.import_from_aqwa(
    file_path="data/vessel.lis",
    vessel_name="FPSO"

*See sub-skills for full details.*
### AQWA File Reading

```python
from digitalmodel.marine_ops.marine_analysis.aqwa_reader import AQWAReader

# Initialize reader
reader = AQWAReader()

# Read AQWA .lis file
aqwa_data = reader.read_lis_file("data/vessel_aqwa.lis")

# Extract motion RAOs

*See sub-skills for full details.*
### OrcaFlex RAO Reading

```python
from digitalmodel.marine_ops.marine_analysis.orcaflex_reader import OrcaFlexRAOReader

# Initialize reader
reader = OrcaFlexRAOReader()

# Read from OrcaFlex model
rao_data = reader.read_from_model("models/vessel_model.yml")

# Or read from vessel type definition
rao_data = reader.read_vessel_type("data/vessel_types/fpso_type.yml")
```
### RAO Validation

```python
from digitalmodel.marine_ops.marine_analysis.rao_validators import RAOValidator

# Initialize validator
validator = RAOValidator()

# Define validation limits
limits = {
    "surge": 10.0,
    "sway": 10.0,

*See sub-skills for full details.*
### RAO Interpolation

```python
from digitalmodel.marine_ops.marine_analysis.rao_interpolator import RAOInterpolator

# Initialize interpolator
interpolator = RAOInterpolator()

# Define target grid
target_frequencies = np.linspace(0.02, 2.0, 100)
target_headings = np.arange(0, 181, 15)


*See sub-skills for full details.*
### Export to OrcaFlex Format

```python
from digitalmodel.marine_ops.marine_analysis.rao_processor import RAOProcessor

processor = RAOProcessor()

# Export to OrcaFlex YAML format
processor.export_to_orcaflex(
    rao_data,
    output_file="vessel_type.yml",
    vessel_name="FPSO_RAOs",

*See sub-skills for full details.*
### Complete Workflow

```python
from digitalmodel.marine_ops.marine_analysis.rao_processor import RAOProcessor
from digitalmodel.marine_ops.marine_analysis.rao_validators import RAOValidator
from digitalmodel.marine_ops.marine_analysis.rao_interpolator import RAOInterpolator

# 1. Import RAOs
processor = RAOProcessor()
raw_raos = processor.import_from_aqwa("data/vessel.lis")

# 2. Validate

*See sub-skills for full details.*

## Related Skills

- [orcaflex-modeling](../orcaflex-modeling/SKILL.md) - Apply imported RAOs
- [orcawave-analysis](../orcawave-analysis/SKILL.md) - Generate RAOs from diffraction
- [aqwa-analysis](../aqwa-analysis/SKILL.md) - AQWA-specific processing
- [hydrodynamics](../hydrodynamics/SKILL.md) - Hydrodynamic coefficient management

## References

- OrcaFlex: Vessel Type RAO Data
- ANSYS AQWA: Output File Formats
- Source: `src/digitalmodel/modules/marine_analysis/rao_processor.py`
- Source: `src/digitalmodel/modules/marine_analysis/aqwa_reader.py`
- Source: `src/digitalmodel/modules/marine_analysis/orcaflex_reader.py`
- User Story: `.ai/specs/modules/user-story-rao-data-import-processing-2025.md`

## Sub-Skills

- [Basic Import Configuration (+1)](basic-import-configuration/SKILL.md)
- [Data Quality (+2)](data-quality/SKILL.md)

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [[1.0.0] - 2026-01-17](100-2026-01-17/SKILL.md)
- [Supported Formats](supported-formats/SKILL.md)
- [6-DOF Motion RAOs](6-dof-motion-raos/SKILL.md)
- [OrcaFlex YAML Format (+2)](orcaflex-yaml-format/SKILL.md)
- [AQWA Import (+1)](aqwa-import/SKILL.md)
