---
name: mesh-utilities-batch-quality-check
description: 'Sub-skill of mesh-utilities: Batch Quality Check (+1).'
version: 1.0.0
category: engineering-utilities
type: reference
scripts_exempt: true
---

# Batch Quality Check (+1)

## Batch Quality Check


```python
from pathlib import Path

def batch_quality_check(mesh_dir: str, pattern: str = "*.gdf") -> dict:
    """Run quality checks on multiple meshes.

    Args:
        mesh_dir: Directory containing meshes
        pattern: Glob pattern for mesh files


*See sub-skills for full details.*

## Batch Conversion


```python
def batch_convert(
    input_dir: str,
    input_pattern: str,
    output_format: str,
    output_dir: str
) -> list:
    """Convert multiple meshes to a target format.

    Args:

*See sub-skills for full details.*
