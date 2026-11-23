---
name: orcaflex-file-conversion
description: Convert OrcaFlex files between formats (.dat, .yml, .sim) for digital
  analysis and automation. Supports bidirectional conversion, batch processing, and
  format standardization.
type: reference
version: 1.0.0
updated: 2026-01-02
category: engineering
triggers:
- convert OrcaFlex files
- .dat to .yml conversion
- .yml to .dat conversion
- .sim to .dat conversion
- .sim to .yml conversion
- OrcaFlex file format conversion
- batch OrcaFlex conversion
- digitally analyze OrcaFlex files
capabilities: []
requires: []
tags: []
scripts_exempt: true
---

# Orcaflex File Conversion

## When to Use

- Converting .dat files to .yml for human-readable inspection
- Converting .yml files back to .dat for OrcaFlex execution
- Converting .sim files to both .dat and .yml formats
- Batch processing multiple OrcaFlex files
- Preparing files for digital analysis and automation
- Creating version-control-friendly YAML representations
- Standardizing file formats across projects

## Prerequisites

- OrcaFlex license (for OrcFxAPI)
- Python environment with `digitalmodel` package installed
- OrcFxAPI Python module configured

## Quick Start

### Single File Conversion

```bash
# Convert .dat to .yml
python -m digitalmodel.solvers.orcaflex.orcaflex_yml_converter model.dat

# Convert .yml to .dat
python -m digitalmodel.solvers.orcaflex.orcaflex_yml_converter model.yml
```
### Batch Conversion

```bash
# Convert all .dat files in directory
python -m digitalmodel.solvers.orcaflex.examples_integration.batch_converter \
    --input-dir models/ \
    --output-dir models_yml/ \
    --pattern "*.dat"

# Convert with validation
python -m digitalmodel.solvers.orcaflex.examples_integration.batch_converter \
    --input-dir models/ \
    --output-dir models_yml/ \
    --validate \
    --max-retries 3
```

## Python API

### Basic Conversion

```python
from digitalmodel.solvers.orcaflex.orcaflex_yml_converter import convert_to_yml
from pathlib import Path

# Convert single file
success = convert_to_yml("model.dat")

# Check output
if success:
    yml_file = Path("model.yml")
    print(f"Converted to: {yml_file}")
```
### Batch Conversion with Progress Tracking

```python
from digitalmodel.solvers.orcaflex.examples_integration.batch_converter import OrcaFlexBatchConverter
from pathlib import Path

# Initialize converter
converter = OrcaFlexBatchConverter(
    input_dir=Path("models/"),
    output_dir=Path("models_yml/"),
    use_mock=False,      # Use real OrcFxAPI
    validate=True,       # Validate converted files

*See sub-skills for full details.*
### Advanced: Bidirectional Conversion

```python
import OrcFxAPI
from pathlib import Path

def convert_yml_to_dat(yml_file: str, dat_file: str = None):
    """Convert YAML to binary .dat format."""
    yml_path = Path(yml_file)

    # Default output path
    if dat_file is None:

*See sub-skills for full details.*
### Simulation File Conversion

```python
from digitalmodel.solvers.orcaflex.examples_integration.orcfxapi_converter import OrcFxAPIConverter
from pathlib import Path

# Initialize converter for .sim files
converter = OrcFxAPIConverter(
    input_dir=Path("results/.sim/"),
    preserve_originals=True
)


*See sub-skills for full details.*

## Related Skills

- orcaflex-modeling - Run OrcaFlex simulations
- orcaflex-post-processing - Process simulation results

## References

- Existing Converters:
  - `src/digitalmodel/solvers/orcaflex/orcaflex_yml_converter.py`
  - `src/digitalmodel/solvers/orcaflex/examples_integration/batch_converter.py`
  - `src/digitalmodel/solvers/orcaflex/examples_integration/orcfxapi_converter.py`
- OrcFxAPI Documentation
- YAML Specification: https://yaml.org/

---

## Version History

- **1.0.0** (2026-01-02): Initial release with bidirectional conversion, batch processing, and comprehensive reporting

## Sub-Skills

- Batch Converter Options (+1)
- File Organization (+1)

## Sub-Skills

- Version Metadata
- [1.0.0] - 2026-01-07
- OrcaFlex File Types (+1)
- Pattern-Based Conversion (+1)
- Conversion Report (Markdown)
- Summary
- Success Rate: 98.9%
- Conversion Report (JSON)
- Example OrcaFlex YAML Output
- YAML Structure Validation (+1)
- Adding Conversion to Universal CLI
- 1. Version Control Preparation (+3)
- Common Issues
- Benchmarks (+1)
