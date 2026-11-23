---
name: instrument-data-allotrope-example-1-vi-cell-blu-file
description: 'Sub-skill of instrument-data-allotrope: Example 1: Vi-CELL BLU file
  (+2).'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# Example 1: Vi-CELL BLU file (+2)

## Example 1: Vi-CELL BLU file

```
User: "Convert this cell counting data to Allotrope format"
[uploads viCell_Results.xlsx]

Claude:
1. Detects Vi-CELL BLU (95% confidence)
2. Converts using allotropy native parser
3. Outputs:
   - viCell_Results_asm.json (full ASM)
   - viCell_Results_flat.csv (2D format)
   - viCell_parser.py (exportable code)
```


## Example 2: Request for code handoff

```
User: "I need to give our data engineer code to parse NanoDrop files"

Claude:
1. Generates self-contained Python script
2. Includes sample input/output
3. Documents all assumptions
4. Provides Jupyter notebook version
```


## Example 3: LIMS-ready flattened output

```
User: "Convert this ELISA data to a CSV I can upload to our LIMS"

Claude:
1. Parses plate reader data
2. Generates flattened CSV with columns:
   - sample_identifier, well_position, measurement_value, measurement_unit
   - instrument_serial_number, analysis_datetime, assay_type
3. Validates against common LIMS import requirements
```
