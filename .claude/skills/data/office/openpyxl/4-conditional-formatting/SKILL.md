---
name: openpyxl-4-conditional-formatting
description: 'Sub-skill of openpyxl: 4. Conditional Formatting.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 4. Conditional Formatting

## 4. Conditional Formatting


```python
"""
Apply conditional formatting rules for visual data analysis.
"""
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Border, Side
from openpyxl.formatting.rule import (
    ColorScaleRule, DataBarRule, IconSetRule,
    CellIsRule, FormulaRule, Rule
)
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.utils import get_column_letter

def create_conditional_formatting_workbook(output_path: str) -> None:
    """Create workbook demonstrating conditional formatting."""
    wb = Workbook()

    # Sheet 1: Color Scales
    ws1 = wb.active
    ws1.title = "Color Scales"

    # Header
    ws1['A1'] = "Performance Scores"
    ws1['A1'].font = Font(bold=True, size=14)

    # Data
    scores = [85, 72, 91, 68, 95, 78, 82, 60, 88, 75, 93, 71, 86, 79, 64]
    for i, score in enumerate(scores, start=3):
        ws1.cell(row=i, column=1, value=f"Employee {i-2}")
        ws1.cell(row=i, column=2, value=score)

    # Apply 3-color scale (red-yellow-green)
    color_scale_rule = ColorScaleRule(
        start_type='min',
        start_color='F8696B',  # Red
        mid_type='percentile',
        mid_value=50,
        mid_color='FFEB84',  # Yellow
        end_type='max',
        end_color='63BE7B'  # Green
    )
    ws1.conditional_formatting.add('B3:B17', color_scale_rule)

    # Sheet 2: Data Bars
    ws2 = wb.create_sheet("Data Bars")

    ws2['A1'] = "Sales by Region"
    ws2['A1'].font = Font(bold=True, size=14)

    regions = [
        ("North", 125000),
        ("South", 98000),
        ("East", 145000),
        ("West", 112000),
        ("Central", 87000),
    ]

    for i, (region, sales) in enumerate(regions, start=3):
        ws2.cell(row=i, column=1, value=region)
        ws2.cell(row=i, column=2, value=sales)

    # Apply data bars
    data_bar_rule = DataBarRule(
        start_type='num',
        start_value=0,
        end_type='max',
        color='5B9BD5',
        showValue=True,
        minLength=None,
        maxLength=None
    )
    ws2.conditional_formatting.add('B3:B7', data_bar_rule)

    # Set column width for visibility
    ws2.column_dimensions['B'].width = 25

    # Sheet 3: Icon Sets
    ws3 = wb.create_sheet("Icon Sets")

    ws3['A1'] = "Project Status"
    ws3['A1'].font = Font(bold=True, size=14)

    # Headers
    ws3['A2'] = "Project"
    ws3['B2'] = "Completion %"
    ws3['C2'] = "Status"

    projects = [
        ("Project Alpha", 95),
        ("Project Beta", 60),
        ("Project Gamma", 30),
        ("Project Delta", 85),
        ("Project Epsilon", 45),
    ]

    for i, (project, completion) in enumerate(projects, start=3):
        ws3.cell(row=i, column=1, value=project)
        ws3.cell(row=i, column=2, value=completion / 100)
        ws3.cell(row=i, column=2).number_format = '0%'

    # Apply icon set (3 traffic lights)
    icon_set_rule = IconSetRule(
        '3TrafficLights1',
        'percent',
        [0, 33, 67],
        showValue=True,
        reverse=False
    )
    ws3.conditional_formatting.add('B3:B7', icon_set_rule)

    # Sheet 4: Cell Rules
    ws4 = wb.create_sheet("Cell Rules")

    ws4['A1'] = "Inventory Status"
    ws4['A1'].font = Font(bold=True, size=14)

    # Headers
    for col, header in enumerate(['Product', 'Stock', 'Reorder Level', 'Status'], start=1):
        ws4.cell(row=2, column=col, value=header).font = Font(bold=True)

    inventory = [
        ("Widget A", 150, 50),
        ("Widget B", 25, 50),
        ("Widget C", 80, 50),
        ("Widget D", 10, 50),
        ("Widget E", 200, 50),
    ]

    for i, (product, stock, reorder) in enumerate(inventory, start=3):
        ws4.cell(row=i, column=1, value=product)
        ws4.cell(row=i, column=2, value=stock)
        ws4.cell(row=i, column=3, value=reorder)

    # Highlight cells below reorder level
    red_fill = PatternFill(start_color='FFC7CE', fill_type='solid')
    red_font = Font(color='9C0006')

    ws4.conditional_formatting.add(
        'B3:B7',
        CellIsRule(
            operator='lessThan',
            formula=['C3'],
            fill=red_fill,
            font=red_font
        )
    )

    # Highlight cells above 100 with green
    green_fill = PatternFill(start_color='C6EFCE', fill_type='solid')
    green_font = Font(color='006100')

    ws4.conditional_formatting.add(
        'B3:B7',
        CellIsRule(
            operator='greaterThan',
            formula=['100'],
            fill=green_fill,
            font=green_font
        )
    )

    # Sheet 5: Formula-based Rules
    ws5 = wb.create_sheet("Formula Rules")

    ws5['A1'] = "Highlight Entire Rows"
    ws5['A1'].font = Font(bold=True, size=14)

    # Headers
    for col, header in enumerate(['Name', 'Dept', 'Salary', 'Status'], start=1):
        ws5.cell(row=2, column=col, value=header).font = Font(bold=True)

    employees = [
        ("Alice", "Engineering", 95000, "Active"),
        ("Bob", "Marketing", 72000, "Inactive"),
        ("Carol", "Engineering", 88000, "Active"),
        ("David", "Sales", 65000, "Inactive"),
        ("Eve", "Engineering", 102000, "Active"),
    ]

    for i, (name, dept, salary, status) in enumerate(employees, start=3):
        ws5.cell(row=i, column=1, value=name)
        ws5.cell(row=i, column=2, value=dept)
        ws5.cell(row=i, column=3, value=salary)
        ws5.cell(row=i, column=4, value=status)

*Content truncated — see parent skill for full reference.*
