---
name: openpyxl-6-pivot-table-creation
description: 'Sub-skill of openpyxl: 6. Pivot Table Creation.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 6. Pivot Table Creation

## 6. Pivot Table Creation


```python
"""
Create pivot table structures in Excel (note: full pivot table functionality
requires Excel to be installed and opened).
"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from typing import List, Dict, Any
from collections import defaultdict

def create_pivot_like_table(
    data: List[Dict[str, Any]],
    row_field: str,
    col_field: str,
    value_field: str,
    aggregation: str = 'sum'
) -> Dict[str, Dict[str, float]]:
    """Create pivot table structure from data."""
    pivot_data = defaultdict(lambda: defaultdict(float))
    row_totals = defaultdict(float)
    col_totals = defaultdict(float)
    grand_total = 0

    for record in data:
        row_val = record[row_field]
        col_val = record[col_field]
        value = record[value_field]

        if aggregation == 'sum':
            pivot_data[row_val][col_val] += value
            row_totals[row_val] += value
            col_totals[col_val] += value
            grand_total += value
        elif aggregation == 'count':
            pivot_data[row_val][col_val] += 1
            row_totals[row_val] += 1
            col_totals[col_val] += 1
            grand_total += 1

    return {
        'data': dict(pivot_data),
        'row_totals': dict(row_totals),
        'col_totals': dict(col_totals),
        'grand_total': grand_total
    }


def write_pivot_table_to_excel(
    wb: Workbook,
    pivot_result: Dict,
    sheet_name: str,
    title: str
) -> None:
    """Write pivot table result to Excel sheet."""
    ws = wb.create_sheet(sheet_name)

    # Styles
    header_fill = PatternFill(start_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    total_fill = PatternFill(start_color="D9E2F3", fill_type="solid")
    total_font = Font(bold=True)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Title
    ws['A1'] = title
    ws['A1'].font = Font(bold=True, size=14)
    ws.merge_cells('A1:E1')

    pivot_data = pivot_result['data']
    row_totals = pivot_result['row_totals']
    col_totals = pivot_result['col_totals']
    grand_total = pivot_result['grand_total']

    # Get unique columns and rows
    all_cols = sorted(set(col for row_data in pivot_data.values() for col in row_data.keys()))
    all_rows = sorted(pivot_data.keys())

    # Write column headers
    start_row = 3
    ws.cell(row=start_row, column=1, value="").border = border

    for col_idx, col_name in enumerate(all_cols, start=2):
        cell = ws.cell(row=start_row, column=col_idx, value=col_name)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
        cell.border = border

    # Total column header
    total_col = len(all_cols) + 2
    cell = ws.cell(row=start_row, column=total_col, value="Total")
    cell.fill = header_fill
    cell.font = header_font
    cell.border = border

    # Write data rows
    for row_idx, row_name in enumerate(all_rows, start=start_row + 1):
        # Row header
        cell = ws.cell(row=row_idx, column=1, value=row_name)
        cell.fill = header_fill
        cell.font = header_font
        cell.border = border

        # Data cells
        for col_idx, col_name in enumerate(all_cols, start=2):
            value = pivot_data[row_name].get(col_name, 0)
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.number_format = '#,##0.00'
            cell.border = border

        # Row total
        cell = ws.cell(row=row_idx, column=total_col, value=row_totals[row_name])
        cell.fill = total_fill
        cell.font = total_font
        cell.number_format = '#,##0.00'
        cell.border = border

    # Write totals row
    totals_row = start_row + len(all_rows) + 1
    cell = ws.cell(row=totals_row, column=1, value="Total")
    cell.fill = header_fill
    cell.font = header_font
    cell.border = border

    for col_idx, col_name in enumerate(all_cols, start=2):
        cell = ws.cell(row=totals_row, column=col_idx, value=col_totals[col_name])
        cell.fill = total_fill
        cell.font = total_font
        cell.number_format = '#,##0.00'
        cell.border = border

    # Grand total
    cell = ws.cell(row=totals_row, column=total_col, value=grand_total)
    cell.fill = total_fill
    cell.font = total_font
    cell.number_format = '#,##0.00'
    cell.border = border

    # Adjust column widths
    for col_idx in range(1, total_col + 1):
        ws.column_dimensions[get_column_letter(col_idx)].width = 15


def create_pivot_table_example(output_path: str) -> None:
    """Create example workbook with pivot table."""
    # Sample data
    sales_data = [
        {"Product": "Widget A", "Region": "North", "Sales": 15000},
        {"Product": "Widget A", "Region": "South", "Sales": 12000},
        {"Product": "Widget A", "Region": "East", "Sales": 18000},
        {"Product": "Widget B", "Region": "North", "Sales": 8000},
        {"Product": "Widget B", "Region": "South", "Sales": 9500},
        {"Product": "Widget B", "Region": "East", "Sales": 7200},
        {"Product": "Widget C", "Region": "North", "Sales": 22000},
        {"Product": "Widget C", "Region": "South", "Sales": 19000},
        {"Product": "Widget C", "Region": "East", "Sales": 25000},
    ]

    wb = Workbook()

    # Raw data sheet
    ws_data = wb.active
    ws_data.title = "Raw Data"

    headers = ["Product", "Region", "Sales"]
    ws_data.append(headers)
    for row in sales_data:
        ws_data.append([row["Product"], row["Region"], row["Sales"]])

    # Create pivot table
    pivot_result = create_pivot_like_table(
        sales_data,
        row_field="Product",
        col_field="Region",
        value_field="Sales",
        aggregation="sum"
    )


*Content truncated — see parent skill for full reference.*
