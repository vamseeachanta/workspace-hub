---
name: orcaflex-file-conversion-pattern-based-conversion
description: 'Sub-skill of orcaflex-file-conversion: Pattern-Based Conversion (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Pattern-Based Conversion (+1)

## Pattern-Based Conversion


```python
from pathlib import Path
from digitalmodel.orcaflex.examples_integration.batch_converter import OrcaFlexBatchConverter

converter = OrcaFlexBatchConverter(
    input_dir=Path("docs/modules/orcaflex/examples/raw"),
    output_dir=Path("docs/modules/orcaflex/examples/yaml"),
    validate=True
)


*See sub-skills for full details.*

## Parallel Processing


```python
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

def convert_file_wrapper(file_path):
    """Wrapper for parallel conversion."""
    from digitalmodel.orcaflex.orcaflex_yml_converter import convert_to_yml
    return convert_to_yml(str(file_path))

# Get all .dat files

*See sub-skills for full details.*
