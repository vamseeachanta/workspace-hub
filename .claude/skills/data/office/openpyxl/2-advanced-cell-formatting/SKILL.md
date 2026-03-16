---
name: openpyxl-2-advanced-cell-formatting
description: 'Sub-skill of openpyxl: 2. Advanced Cell Formatting.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 2. Advanced Cell Formatting

## 2. Advanced Cell Formatting


```python
"""
Advanced cell formatting with styles, merging, and data validation.
"""
from openpyxl import Workbook
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side,
    GradientFill, NamedStyle, Color
)
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.formatting.rule import Rule, CellIsRule, FormulaRule
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

def create_formatted_workbook(output_path: str) -> None:
    """Create workbook with advanced formatting."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Formatted Data"

    # Create named styles for reuse
    header_style = NamedStyle(name="header_style")
    header_style.font = Font(bold=True, color="FFFFFF", size=11)
    header_style.fill = PatternFill(start_color="2F5496", fill_type="solid")
    header_style.alignment = Alignment(horizontal="center", vertical="center")
    header_style.border = Border(
        bottom=Side(style='medium', color="1F4E79")
    )
    wb.add_named_style(header_style)

    currency_style = NamedStyle(name="currency_style")
    currency_style.number_format = '"$"#,##0.00'
    currency_style.alignment = Alignment(horizontal="right")
    wb.add_named_style(currency_style)

    percentage_style = NamedStyle(name="percentage_style")
    percentage_style.number_format = '0.0%'
    percentage_style.alignment = Alignment(horizontal="center")
    wb.add_named_style(percentage_style)

    # Title with merged cells
    ws.merge_cells('A1:F1')
    title_cell = ws['A1']
    title_cell.value = "Financial Summary Report"
    title_cell.font = Font(bold=True, size=16, color="1F4E79")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30

    # Subtitle
    ws.merge_cells('A2:F2')
    subtitle_cell = ws['A2']
    subtitle_cell.value = "Fiscal Year 2026"
    subtitle_cell.font = Font(italic=True, size=12, color="5B9BD5")
    subtitle_cell.alignment = Alignment(horizontal="center")
    ws.row_dimensions[2].height = 20

    # Headers row
    headers = ["Category", "Budget", "Actual", "Variance", "% of Budget", "Status"]
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=4, column=col, value=header)
        cell.style = "header_style"

    # Data with various formats
    data = [
        ["Revenue", 1000000, 1150000],
        ["Personnel", 500000, 485000],
        ["Operations", 200000, 215000],
        ["Marketing", 150000, 142000],
        ["Technology", 100000, 108000],
    ]

    for row_idx, (category, budget, actual) in enumerate(data, start=5):
        # Category
        ws.cell(row=row_idx, column=1, value=category)

        # Budget
        ws.cell(row=row_idx, column=2, value=budget).style = "currency_style"

        # Actual
        ws.cell(row=row_idx, column=3, value=actual).style = "currency_style"

        # Variance formula
        variance_cell = ws.cell(row=row_idx, column=4)
        variance_cell.value = f"=C{row_idx}-B{row_idx}"
        variance_cell.style = "currency_style"

        # Percentage formula
        pct_cell = ws.cell(row=row_idx, column=5)
        pct_cell.value = f"=C{row_idx}/B{row_idx}"
        pct_cell.style = "percentage_style"

        # Status (will be filled by conditional formatting)
        ws.cell(row=row_idx, column=6, value="")

    # Add conditional formatting for variance column
    # Green for positive, red for negative
    green_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
    red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

    ws.conditional_formatting.add(
        'D5:D9',
        CellIsRule(
            operator='greaterThan',
            formula=['0'],
            fill=green_fill,
            font=Font(color="006100")
        )
    )

    ws.conditional_formatting.add(
        'D5:D9',
        CellIsRule(
            operator='lessThan',
            formula=['0'],
            fill=red_fill,
            font=Font(color="9C0006")
        )
    )

    # Data validation for status column
    status_validation = DataValidation(
        type="list",
        formula1='"On Track,At Risk,Over Budget,Under Budget"',
        allow_blank=True
    )
    status_validation.error = "Please select from the dropdown"
    status_validation.errorTitle = "Invalid Status"
    ws.add_data_validation(status_validation)
    status_validation.add('F5:F9')

    # Gradient fill example
    ws['A12'] = "Gradient Fill Example"
    ws['A12'].fill = GradientFill(
        stop=["4472C4", "70AD47"],
        degree=90
    )
    ws['A12'].font = Font(color="FFFFFF", bold=True)
    ws.merge_cells('A12:C12')

    # Column widths
    widths = {'A': 15, 'B': 15, 'C': 15, 'D': 15, 'E': 15, 'F': 15}
    for col, width in widths.items():
        ws.column_dimensions[col].width = width

    wb.save(output_path)
    print(f"Formatted workbook saved to {output_path}")


create_formatted_workbook("formatted_report.xlsx")
```
