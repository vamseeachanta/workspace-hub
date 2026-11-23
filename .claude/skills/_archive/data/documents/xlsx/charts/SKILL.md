---
name: xlsx-charts
description: 'Sub-skill of xlsx: Charts.'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Charts

## Charts


```python
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference

wb = Workbook()
ws = wb.active

# Data
data = [
    ["Month", "Sales"],
    ["Jan", 100],
    ["Feb", 120],
    ["Mar", 140],
    ["Apr", 110],
]
for row in data:
    ws.append(row)

# Create chart
chart = BarChart()
chart.type = "col"
chart.title = "Monthly Sales"
chart.y_axis.title = "Sales ($)"
chart.x_axis.title = "Month"


*See sub-skills for full details.*
