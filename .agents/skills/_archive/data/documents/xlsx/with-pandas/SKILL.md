---
name: xlsx-with-pandas
description: 'Sub-skill of xlsx: With Pandas (+1).'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# With Pandas (+1)

## With Pandas


```python
import pandas as pd

df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Sales': [1000, 1500, 1200],
    'Region': ['East', 'West', 'North']
})

# Simple export

*See sub-skills for full details.*

## With Openpyxl (Formulas)


```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

wb = Workbook()
ws = wb.active
ws.title = "Financial Model"

# Headers

*See sub-skills for full details.*
