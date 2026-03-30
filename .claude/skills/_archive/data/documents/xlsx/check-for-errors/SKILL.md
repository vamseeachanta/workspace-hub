---
name: xlsx-check-for-errors
description: 'Sub-skill of xlsx: Check for Errors (+1).'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Check for Errors (+1)

## Check for Errors


```python
from openpyxl import load_workbook

wb = load_workbook("model.xlsx", data_only=False)
ws = wb.active

errors = ["#REF!", "#DIV/0!", "#VALUE!", "#N/A", "#NAME?", "#NULL!", "#NUM!"]

for row in ws.iter_rows():
    for cell in row:
        if cell.value and isinstance(cell.value, str):
            for error in errors:
                if error in str(cell.value):
                    print(f"Error {error} in cell {cell.coordinate}")
```

## Validate Formulas


Before saving, always:
1. Check cell references are correct
2. Avoid off-by-one errors
3. Test edge cases (empty cells, zeros)
4. Verify formula logic
