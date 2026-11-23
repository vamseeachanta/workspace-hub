---
name: bemrosetta
description: BEMRosetta hydrodynamic coefficient converter - AQWA to OrcaFlex workflow
  with QTF and mesh support
type: reference
version: 1.0.0
updated: 2026-01-27
category: engineering
triggers:
- bemrosetta
- hydrodynamic conversion
- AQWA to OrcaFlex
- coefficient converter
- QTF conversion
- mesh format conversion
- GDF to STL
- panel mesh
- Kramers-Kronig
- causality check
capabilities: []
requires: []
tags: []
scripts_exempt: true
---

# Bemrosetta

## When to Use

Use this skill when you need to:

1. **Convert AQWA outputs to OrcaFlex format**
   - Parse AQWA .LIS diffraction analysis files
   - Export to OrcaFlex-compatible YAML and CSV

2. **Handle QTF (second-order forces) data**
   - Parse QTF files for sum/difference frequency forces
   - Export QTF to OrcaFlex format

3. **Convert mesh formats**
   - Convert between GDF (WAMIT), DAT (AQWA/NEMOH), STL formats
   - Validate mesh quality

4. **Validate hydrodynamic coefficients**
   - Check matrix symmetry and positive definiteness
   - Verify Kramers-Kronig causality relations

## Prerequisites

```bash
# Module is included in digitalmodel package
uv pip install -e .

# Verify installation
bemrosetta status
```

## Python API

### Basic Workflow

```python
from digitalmodel.bemrosetta import (
    AQWAParser,
    OrcaFlexConverter,
    validate_coefficients,
)

# Parse AQWA results
parser = AQWAParser()
results = parser.parse("analysis.LIS")

*See sub-skills for full details.*
### QTF Handling

```python
from digitalmodel.bemrosetta import QTFParser, OrcaFlexConverter

# Parse QTF file
qtf_parser = QTFParser()
qtf_data = qtf_parser.parse("analysis.QTF")

print(f"QTF type: {qtf_data.qtf_type}")
print(f"Frequencies: {qtf_data.n_frequencies_1} x {qtf_data.n_frequencies_2}")

# Include QTF in conversion
converter = OrcaFlexConverter(output_dir="./output")
converter.set_qtf_data(qtf_data)
converter.convert(results)
```
### Mesh Conversion

```python
from digitalmodel.bemrosetta import (
    GDFHandler, DATHandler, STLHandler, convert_mesh
)

# Read GDF mesh
handler = GDFHandler()
mesh = handler.read("hull.gdf")

# Check quality

*See sub-skills for full details.*
### Causality Validation

```python
from digitalmodel.bemrosetta import (
    CoefficientValidator,
    CausalityChecker,
)

# Coefficient validation
validator = CoefficientValidator(
    check_symmetry=True,
    check_positive_definite=True,

*See sub-skills for full details.*

## Key Classes

| Class | Purpose |
|-------|---------|
| `AQWAParser` | Parse AQWA .LIS files |
| `QTFParser` | Parse QTF second-order force files |
| `OrcaFlexConverter` | Convert to OrcaFlex format |
| `GDFHandler` | WAMIT GDF mesh format |
| `DATHandler` | AQWA/NEMOH DAT mesh format |
| `STLHandler` | STL mesh format |
| `CoefficientValidator` | Validate coefficient matrices |
| `CausalityChecker` | Kramers-Kronig validation |

## Related Skills

- **aqwa-analysis** - AQWA .LIS processing and RAO extraction
- **orcawave/analysis** - OrcaWave diffraction/radiation analysis
- **orcawave/to-orcaflex** - OrcaWave to OrcaFlex conversion
- **orcaflex/rao-import** - Multi-format RAO import
- **hydrodynamics** - 6x6 matrices and wave spectra
- **diffraction-analysis** - Master skill for diffraction workflows

## References

- [BEMRosetta GitHub](https://github.com/BEMRosetta/BEMRosetta)
- [Module README](../../../src/digitalmodel/modules/bemrosetta/MODULE_README.md)
- [OrcaFlex Documentation](https://www.orcina.com/webhelp/OrcaFlex/)

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)
- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [Version](version/SKILL.md)
- [1.0.0 (2026-01-27)](100-2026-01-27/SKILL.md)
- [Parsing (+3)](parsing/SKILL.md)
- [CLI Commands](cli-commands/SKILL.md)
- [Data Models](data-models/SKILL.md)
- [With diffraction module (+1)](with-diffraction-module/SKILL.md)
