---
name: openpyxl-common-issues
description: 'Sub-skill of openpyxl: Common Issues.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


#### 1. Formula Not Calculating

```python
# Problem: Formulas show as text, not calculated
# Solution: Ensure proper formula format

# DO: Use equals sign and proper cell references
ws['A1'] = '=SUM(B1:B10)'

# DON'T: Use string that looks like formula
# ws['A1'] = 'SUM(B1:B10)'  # Missing =

# Note: Formulas are calculated when Excel opens the file
```

#### 2. Large File Performance

```python
# Problem: Memory error with large files
# Solution: Use streaming modes

# For writing
wb = Workbook(write_only=True)

# For reading
wb = load_workbook('file.xlsx', read_only=True, data_only=True)
```

#### 3. Style Not Appearing

```python
# Problem: Styles don't appear in Excel
# Solution: Ensure style is properly applied

# DO: Apply fill with fill_type
fill = PatternFill(start_color="FF0000", fill_type="solid")

# DON'T: Missing fill_type
# fill = PatternFill(start_color="FF0000")  # Won't show
```
