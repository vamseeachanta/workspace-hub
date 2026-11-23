---
name: instrument-data-allotrope-code-export-for-data-engineers
description: 'Sub-skill of instrument-data-allotrope: Code Export for Data Engineers.'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# Code Export for Data Engineers

## Code Export for Data Engineers


Generate standalone Python scripts that scientists can hand off:

```python
# Export parser code
python scripts/export_parser.py --input "data.csv" --vendor "VI_CELL_BLU" --output "parser_script.py"
```

The exported script:
- Has no external dependencies beyond pandas/allotropy
- Includes inline documentation
- Can run in Jupyter notebooks
- Is production-ready for data pipelines
