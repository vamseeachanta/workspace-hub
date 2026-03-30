---
name: openpyxl-1-basic-workbook-creation
description: 'Sub-skill of openpyxl: 1. Basic Workbook Creation.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Basic Workbook Creation

## 1. Basic Workbook Creation


```python
"""
Create a basic Excel workbook with data and formatting.
"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime

def create_basic_workbook(output_path: str) -> None:
    """Create a basic workbook with common elements."""
    # Create workbook and select active sheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Sales Report"

    # Set document properties
    wb.properties.creator = "Excel Generator"
    wb.properties.title = "Monthly Sales Report"
    wb.properties.created = datetime.now()

    # Define styles
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")

    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Headers
    headers = ["Product", "Q1", "Q2", "Q3", "Q4", "Total"]
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border

    # Data
    data = [
        ["Widget A", 1500, 1800, 2200, 2500],
        ["Widget B", 800, 950, 1100, 1300],
        ["Widget C", 2000, 2300, 2600, 2900],
        ["Widget D", 500, 600, 750, 900],
    ]

    for row_idx, row_data in enumerate(data, start=2):
        # Product name
        ws.cell(row=row_idx, column=1, value=row_data[0]).border = thin_border

        # Quarterly values
        for col_idx, value in enumerate(row_data[1:], start=2):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.border = thin_border
            cell.number_format = '#,##0'

        # Total formula
        total_cell = ws.cell(
            row=row_idx,
            column=6,
            value=f"=SUM(B{row_idx}:E{row_idx})"
        )
        total_cell.border = thin_border
        total_cell.font = Font(bold=True)
        total_cell.number_format = '#,##0'

    # Add totals row
    total_row = len(data) + 2
    ws.cell(row=total_row, column=1, value="TOTAL").font = Font(bold=True)

    for col in range(2, 7):
        col_letter = get_column_letter(col)
        cell = ws.cell(
            row=total_row,
            column=col,
            value=f"=SUM({col_letter}2:{col_letter}{total_row-1})"
        )
        cell.font = Font(bold=True)
        cell.number_format = '#,##0'
        cell.border = thin_border

    # Adjust column widths
    column_widths = [15, 12, 12, 12, 12, 14]
    for i, width in enumerate(column_widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = width

    # Freeze header row
    ws.freeze_panes = "A2"

    # Save workbook
    wb.save(output_path)
    print(f"Workbook saved to {output_path}")


create_basic_workbook("sales_report.xlsx")
```
