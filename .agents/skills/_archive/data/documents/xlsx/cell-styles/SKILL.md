---
name: xlsx-cell-styles
description: 'Sub-skill of xlsx: Cell Styles (+1).'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Cell Styles (+1)

## Cell Styles


```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.styles.numbers import FORMAT_CURRENCY_USD_SIMPLE

wb = Workbook()
ws = wb.active

# Font styling
ws["A1"] = "Styled Cell"

*See sub-skills for full details.*

## Column Width and Row Height


```python
from openpyxl import Workbook

wb = Workbook()
ws = wb.active

# Set column width
ws.column_dimensions["A"].width = 20
ws.column_dimensions["B"].width = 15


*See sub-skills for full details.*
