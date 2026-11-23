---
name: openpyxl-pandas-integration
description: 'Sub-skill of openpyxl: Pandas Integration (+1).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Pandas Integration (+1)

## Pandas Integration


```python
"""
Integration with pandas for data analysis workflows.
"""
import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font, PatternFill, Alignment

def dataframe_to_styled_excel(
    df: pd.DataFrame,
    output_path: str,
    sheet_name: str = "Data",
    header_color: str = "4472C4"
) -> None:
    """Export pandas DataFrame to styled Excel file."""
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    # Write DataFrame to worksheet
    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True)):
        for c_idx, value in enumerate(row, start=1):
            cell = ws.cell(row=r_idx + 1, column=c_idx, value=value)

            # Style header row
            if r_idx == 0:
                cell.fill = PatternFill(start_color=header_color, fill_type="solid")
                cell.font = Font(bold=True, color="FFFFFF")
                cell.alignment = Alignment(horizontal="center")

    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        ws.column_dimensions[column_letter].width = min(max_length + 2, 50)

    wb.save(output_path)
    print(f"DataFrame exported to {output_path}")


def excel_to_dataframe_with_types(
    file_path: str,
    sheet_name: str = None,
    dtype_mapping: dict = None
) -> pd.DataFrame:
    """Read Excel file to pandas DataFrame with proper type handling."""
    # Read with openpyxl engine
    df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        engine='openpyxl'
    )

    # Apply type mappings if provided
    if dtype_mapping:
        for col, dtype in dtype_mapping.items():
            if col in df.columns:
                df[col] = df[col].astype(dtype)

    return df


def create_multi_sheet_report(
    dataframes: dict,
    output_path: str
) -> None:
    """Create Excel workbook with multiple DataFrames on separate sheets."""
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for sheet_name, df in dataframes.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Access worksheet for formatting
            ws = writer.sheets[sheet_name]

            # Style header row
            for cell in ws[1]:
                cell.fill = PatternFill(start_color="4472C4", fill_type="solid")
                cell.font = Font(bold=True, color="FFFFFF")

    print(f"Multi-sheet report saved to {output_path}")


# Example usage
# df = pd.DataFrame({'A': [1, 2, 3], 'B': ['x', 'y', 'z']})
# dataframe_to_styled_excel(df, 'output.xlsx')
```


## Database Report Generation


```python
"""
Generate Excel reports from database queries.
"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime
import sqlite3
from typing import List, Tuple, Any

def generate_database_report(
    db_path: str,
    queries: dict,
    output_path: str
) -> None:
    """Generate Excel report from multiple database queries."""
    conn = sqlite3.connect(db_path)
    wb = Workbook()

    # Remove default sheet
    wb.remove(wb.active)

    # Styles
    header_fill = PatternFill(start_color="2F5496", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    for sheet_name, query in queries.items():
        # Execute query
        cursor = conn.execute(query)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        # Create sheet
        ws = wb.create_sheet(sheet_name)

        # Add metadata
        ws['A1'] = f"Report: {sheet_name}"
        ws['A1'].font = Font(bold=True, size=14)
        ws['A2'] = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ws['A2'].font = Font(italic=True, size=10)

        # Write headers
        for col_idx, header in enumerate(columns, start=1):
            cell = ws.cell(row=4, column=col_idx, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")
            cell.border = border

        # Write data
        for row_idx, row in enumerate(rows, start=5):
            for col_idx, value in enumerate(row, start=1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.border = border

                # Format numbers
                if isinstance(value, (int, float)):
                    cell.number_format = '#,##0.00'

        # Auto-fit columns
        for col_idx in range(1, len(columns) + 1):
            ws.column_dimensions[get_column_letter(col_idx)].width = 15

        # Add row count
        ws.cell(row=len(rows) + 6, column=1, value=f"Total rows: {len(rows)}")

    conn.close()
    wb.save(output_path)
    print(f"Database report saved to {output_path}")
```
