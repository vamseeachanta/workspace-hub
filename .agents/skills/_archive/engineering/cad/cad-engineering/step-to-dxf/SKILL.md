---
name: cad-engineering-step-to-dxf
description: 'Sub-skill of cad-engineering: STEP to DXF (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# STEP to DXF (+2)

## STEP to DXF


```python
from digitalmodel.agents.cad import FormatConverter

converter = FormatConverter()

# Convert STEP to DXF with projection
result = converter.convert(
    input_file="model.step",
    output_file="drawing.dxf",
    projection="front",  # top, front, right, isometric

*See sub-skills for full details.*

## DWG Version Conversion


```python
# Convert between DWG versions
result = converter.convert(
    input_file="drawing_2024.dwg",
    output_file="drawing_2010.dwg",
    target_version="2010"  # For compatibility
)
```

## Batch Format Conversion


```python
from digitalmodel.agents.cad import BatchConverter

batch = BatchConverter()

# Convert all STEP files to IGES
results = batch.convert_directory(
    input_directory="./step_files",
    output_directory="./iges_files",
    input_format="STEP",

*See sub-skills for full details.*
