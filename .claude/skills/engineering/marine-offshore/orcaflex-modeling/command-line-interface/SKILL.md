---
name: orcaflex-modeling-command-line-interface
description: 'Sub-skill of orcaflex-modeling: Command Line Interface (+1).'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Command Line Interface (+1)

## Command Line Interface


```bash
# Process all YAML files in current directory
python -m digitalmodel.orcaflex.universal pattern="*.yml"

# Specify input/output directories
python -m digitalmodel.orcaflex.universal \
    pattern="mooring_*.yml" \
    input_directory="configs/" \
    output_directory="results/"


*See sub-skills for full details.*

## Python API


```python
from digitalmodel.orcaflex.universal import UniversalOrcaFlexRunner

# Initialize runner
runner = UniversalOrcaFlexRunner(
    input_directory="configs/",
    output_directory="results/",
    mock_mode=False
)


*See sub-skills for full details.*
