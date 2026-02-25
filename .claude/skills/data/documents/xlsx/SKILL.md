---
name: xlsx
description: Excel spreadsheet toolkit for creating, reading, and manipulating .xlsx files. Supports formulas, formatting, charts, and financial modeling with industry-standard conventions. Use for data analysis, financial models, reports, and spreadsheet automation.
version: 1.1.0
last_updated: 2026-01-02
category: document-handling
related_skills:
  - docx
  - pptx
  - pdf
capabilities: []
requires: []
see_also: []
---

# XLSX Processing Skill

## Overview

Comprehensive Excel manipulation using pandas for data analysis and openpyxl for formulas, formatting, and Excel-specific features.

## Quick Start

```python
import pandas as pd
from openpyxl import Workbook

# Read with pandas
df = pd.read_excel("data.xlsx")
print(df.head())

# Create with openpyxl
wb = Workbook()
ws = wb.active
ws["A1"] = "Hello"
ws["B1"] = "World"
wb.save("output.xlsx")
```

## When to Use

- Reading and analyzing Excel data with pandas
- Creating formatted spreadsheets programmatically
- Building financial models with formulas
- Generating reports with charts and graphs
- Automating data entry and updates
- Converting between Excel and other formats
- Batch processing multiple spreadsheets
- Creating templates for repeated use

## Requirements for All Output

- **Zero formula errors mandatory**
- Preserve existing templates when updating
- Always use Excel formulas instead of calculating values in Python and hardcoding them
- Follow industry-standard color coding for financial models

### Financial Model Color Standards
- **Blue**: Input cells (hardcoded values)
- **Black**: Formula cells (calculated values)
- **Green**: Links to other worksheets
- **Red**: Links to external files

### Number Formatting Rules
- Years displayed as text (no commas)
- Currency with appropriate units (K, M, B)
- Zeros displayed as "-"

## Reading Excel Files

### With Pandas
```python
import pandas as pd

# Read entire file
df = pd.read_excel("data.xlsx")

# Read specific sheet
df = pd.read_excel("data.xlsx", sheet_name="Sheet2")

# Read with options
df = pd.read_excel(
    "data.xlsx",
    sheet_name=0,
    header=0,
    usecols="A:D",
    skiprows=2
)

# Read all sheets
dfs = pd.read_excel("data.xlsx", sheet_name=None)
for sheet_name, df in dfs.items():
    print(f"Sheet: {sheet_name}")
    print(df.head())
```

### With Openpyxl
```python
from openpyxl import load_workbook

wb = load_workbook("data.xlsx")
ws = wb.active

# Read cell values
for row in ws.iter_rows(min_row=1, max_row=10, values_only=True):
    print(row)

# Read specific cell
value = ws["A1"].value
```

## Creating Excel Files

### With Pandas
```python
import pandas as pd

df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Sales': [1000, 1500, 1200],
    'Region': ['East', 'West', 'North']
})

# Simple export
df.to_excel("output.xlsx", index=False)

# Multiple sheets
with pd.ExcelWriter("output.xlsx") as writer:
    df.to_excel(writer, sheet_name="Sales", index=False)
    df.to_excel(writer, sheet_name="Backup", index=False)
```

### With Openpyxl (Formulas)
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

wb = Workbook()
ws = wb.active
ws.title = "Financial Model"

# Headers
headers = ["Item", "Q1", "Q2", "Q3", "Q4", "Total"]
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.font = Font(bold=True)
    cell.alignment = Alignment(horizontal="center")

# Data with formulas
data = [
    ("Revenue", 1000, 1200, 1100, 1400),
    ("Expenses", 800, 900, 850, 1000),
]

for row, (item, *values) in enumerate(data, 2):
    ws.cell(row=row, column=1, value=item)
    for col, value in enumerate(values, 2):
        ws.cell(row=row, column=col, value=value)
    # Total formula
    ws.cell(row=row, column=6, value=f"=SUM(B{row}:E{row})")

# Profit row with formula
ws.cell(row=4, column=1, value="Profit")
for col in range(2, 7):
    col_letter = get_column_letter(col)
    ws.cell(row=4, column=col, value=f"={col_letter}2-{col_letter}3")

wb.save("financial_model.xlsx")
```

## Formatting

### Cell Styles
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.styles.numbers import FORMAT_CURRENCY_USD_SIMPLE

wb = Workbook()
ws = wb.active

# Font styling
ws["A1"] = "Styled Cell"
ws["A1"].font = Font(
    name="Arial",
    size=14,
    bold=True,
    italic=False,
    color="2E74B5"
)

# Fill color
ws["A2"] = "Blue Background"
ws["A2"].fill = PatternFill(
    start_color="0000FF",
    end_color="0000FF",
    fill_type="solid"
)

# Number format
ws["A3"] = 1234567.89
ws["A3"].number_format = FORMAT_CURRENCY_USD_SIMPLE

# Alignment
ws["A4"] = "Centered"
ws["A4"].alignment = Alignment(
    horizontal="center",
    vertical="center"
)

# Borders
thin_border = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin")
)
ws["A5"].border = thin_border

wb.save("formatted.xlsx")
```

### Column Width and Row Height
```python
from openpyxl import Workbook

wb = Workbook()
ws = wb.active

# Set column width
ws.column_dimensions["A"].width = 20
ws.column_dimensions["B"].width = 15

# Set row height
ws.row_dimensions[1].height = 30

# Auto-fit (approximate)
for col in ws.columns:
    max_length = 0
    column = col[0].column_letter
    for cell in col:
        if cell.value:
            max_length = max(max_length, len(str(cell.value)))
    ws.column_dimensions[column].width = max_length + 2

wb.save("sized.xlsx")
```

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

data = Reference(ws, min_col=2, min_row=1, max_row=5)
cats = Reference(ws, min_col=1, min_row=2, max_row=5)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
chart.shape = 4  # Rectangle

ws.add_chart(chart, "D2")
wb.save("with_chart.xlsx")
```

## Formula Verification

### Check for Errors
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

### Validate Formulas
Before saving, always:
1. Check cell references are correct
2. Avoid off-by-one errors
3. Test edge cases (empty cells, zeros)
4. Verify formula logic

## Execution Checklist

- [ ] Choose appropriate tool (pandas vs openpyxl)
- [ ] Verify input file exists and is valid
- [ ] Test formulas with sample data
- [ ] Apply consistent formatting
- [ ] Validate all formulas produce correct results
- [ ] Check for Excel errors (#REF!, #DIV/0!, etc.)
- [ ] Verify charts display correctly
- [ ] Test in Excel/LibreOffice before delivery

## Error Handling

### Common Errors

**Error: InvalidFileException**
- Cause: File is not a valid .xlsx (possibly .xls)
- Solution: Convert to .xlsx or use xlrd for .xls files

**Error: Circular reference**
- Cause: Formula references itself
- Solution: Review formula logic and break the cycle

**Error: #REF! in formulas**
- Cause: Cell reference is invalid (deleted row/column)
- Solution: Use named ranges or validate references

**Error: Memory issues with large files**
- Cause: Loading entire file into memory
- Solution: Use `read_only=True` or `write_only=True` mode

## Metrics

| Metric | Typical Value |
|--------|---------------|
| Read speed (pandas) | ~50,000 rows/second |
| Write speed (pandas) | ~30,000 rows/second |
| Formula cells | ~10,000 cells/second |
| Chart creation | ~5 charts/second |
| Memory usage | ~100MB per 100K rows |

## Workflow

1. Choose appropriate tool (pandas or openpyxl)
2. Create or load workbook
3. Modify as needed
4. Save file
5. **For formula-based files**: Run formula recalculation
6. Verify and fix errors

## Quick Reference

| Task | Tool |
|------|------|
| Data analysis | pandas |
| Simple read/write | pandas |
| Formulas | openpyxl |
| Formatting | openpyxl |
| Charts | openpyxl |
| Pivot tables | Use Excel or xlwings |

## Dependencies

```bash
pip install pandas openpyxl xlrd
```

Optional:
- xlwings (Windows/Mac Excel automation)
- xlsxwriter (alternative writer)

---

## Version History

- **1.1.0** (2026-01-02): Added Quick Start, When to Use, Execution Checklist, Error Handling, Metrics sections; updated frontmatter with version, category, related_skills
- **1.0.0** (2024-10-15): Initial release with pandas, openpyxl, financial model standards
