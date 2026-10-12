---
name: orcaflex-rao-import
description: Import RAO (Response Amplitude Operator) data from external sources including
  AQWA, OrcaFlex, and CSV files. Includes validation, interpolation, and conversion
  for OrcaFlex vessel type creation.
type: reference
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
tags: []
scripts_exempt: true
---

<!-- ace:api-missing-warning -->
> [!WARNING]
> **Part of the Python API documented below does not exist in
> `digitalmodel`.** These snippets are a *specification* of intended
> capability, not runnable code. Do not import them, and do not report
> a result obtained by pretending they ran.
>
> Absent as of this revision:
>   - `digitalmodel.marine_ops.marine_analysis.orcaflex_reader.OrcaFlexRAOReader`
>   - `digitalmodel.marine_ops.marine_analysis.rao_processor.RAOProcessor`
>   - `digitalmodel.marine_ops.marine_analysis.rao_validators.RAOValidator`
>
> The surrounding engineering content — method, conventions, what to
> watch for — is unaffected and remains usable. Tracked in
> aceengineer-strategy#267.

<!-- ace:known-missing: digitalmodel.marine_ops.marine_analysis.orcaflex_reader.OrcaFlexRAOReader, digitalmodel.marine_ops.marine_analysis.rao_processor.RAOProcessor, digitalmodel.marine_ops.marine_analysis.rao_validators.RAOValidator -->

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

- orcaflex-modeling - Apply imported RAOs
- orcawave/analysis - Generate RAOs from diffraction
- aqwa-analysis - AQWA-specific processing
- hydrodynamics - Hydrodynamic coefficient management

## References

- OrcaFlex: Vessel Type RAO Data
- ANSYS AQWA: Output File Formats
- Source: `src/digitalmodel/marine_ops/marine_analysis/rao_processor.py`
- Source: `src/digitalmodel/modules/marine_analysis/aqwa_reader.py`
- Source: `src/digitalmodel/marine_ops/marine_analysis/orcaflex_reader.py`
- User Story: `.ai/specs/modules/user-story-rao-data-import-processing-2025.md`

## Sub-Skills

- Basic Import Configuration (+1)
- Data Quality (+2)

## Sub-Skills

- Error Handling

## Sub-Skills

- Version Metadata
- [1.0.0] - 2026-01-17
- Supported Formats
- 6-DOF Motion RAOs
- OrcaFlex YAML Format (+2)
- AQWA Import (+1)
