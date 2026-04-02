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
python -m digitalmodel.orcaflex.orcaflex_yml_converter model.dat

# Convert .yml to .dat
python -m digitalmodel.orcaflex.orcaflex_yml_converter model.yml
```
### Batch Conversion

```bash
# Convert all .dat files in directory
python -m digitalmodel.orcaflex.examples_integration.batch_converter \
    --input-dir models/ \
    --output-dir models_yml/ \
    --pattern "*.dat"

# Convert with validation
python -m digitalmodel.orcaflex.examples_integration.batch_converter \
    --input-dir models/ \
    --output-dir models_yml/ \
    --validate \
    --max-retries 3
```

## Python API

### Basic Conversion

```python
from digitalmodel.orcaflex.orcaflex_yml_converter import convert_to_yml
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
from digitalmodel.orcaflex.examples_integration.batch_converter import OrcaFlexBatchConverter
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
from digitalmodel.orcaflex.examples_integration.orcfxapi_converter import OrcFxAPIConverter
from pathlib import Path

# Initialize converter for .sim files
converter = OrcFxAPIConverter(
    input_dir=Path("results/.sim/"),
    preserve_originals=True
)


*See sub-skills for full details.*

## Related Skills

- [orcaflex-modeling](../orcaflex-modeling/SKILL.md) - Run OrcaFlex simulations
- [orcaflex-post-processing](../orcaflex-post-processing/SKILL.md) - Process simulation results

## References

- Existing Converters:
  - `src/digitalmodel/modules/orcaflex/orcaflex_yml_converter.py`
  - `src/digitalmodel/modules/orcaflex/examples_integration/batch_converter.py`
  - `src/digitalmodel/modules/orcaflex/examples_integration/orcfxapi_converter.py`
- OrcFxAPI Documentation
- YAML Specification: https://yaml.org/

---

## Version History

- **1.0.0** (2026-01-02): Initial release with bidirectional conversion, batch processing, and comprehensive reporting

## Sub-Skills

- [Batch Converter Options (+1)](batch-converter-options/SKILL.md)
- [File Organization (+1)](file-organization/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [[1.0.0] - 2026-01-07](100-2026-01-07/SKILL.md)
- [OrcaFlex File Types (+1)](orcaflex-file-types/SKILL.md)
- [Pattern-Based Conversion (+1)](pattern-based-conversion/SKILL.md)
- [Conversion Report (Markdown)](conversion-report-markdown/SKILL.md)
- [Summary](summary/SKILL.md)
- [Success Rate: 98.9%](success-rate-989/SKILL.md)
- [Conversion Report (JSON)](conversion-report-json/SKILL.md)
- [Example OrcaFlex YAML Output](example-orcaflex-yaml-output/SKILL.md)
- [YAML Structure Validation (+1)](yaml-structure-validation/SKILL.md)
- [Adding Conversion to Universal CLI](adding-conversion-to-universal-cli/SKILL.md)
- [1. Version Control Preparation (+3)](1-version-control-preparation/SKILL.md)
- [Common Issues](common-issues/SKILL.md)
- [Benchmarks (+1)](benchmarks/SKILL.md)
