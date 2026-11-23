---
name: python-pptx-4-table-creation
description: 'Sub-skill of python-pptx: 4. Table Creation.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 4. Table Creation

## 4. Table Creation


```python
"""
Create and format tables in PowerPoint presentations.
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RgbColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.oxml import parse_xml
from typing import List, Any

def set_cell_color(cell, color_hex: str) -> None:
    """Set cell background color."""
    cell.fill.solid()
    cell.fill.fore_color.rgb = RgbColor(
        int(color_hex[0:2], 16),
        int(color_hex[2:4], 16),
        int(color_hex[4:6], 16)
    )


def create_table_slide(
    prs: Presentation,
    title: str,
    headers: List[str],
    data: List[List[Any]],
    col_widths: List[float] = None
) -> None:
    """Create a slide with a formatted table."""
    slide = prs.slides.add_slide(prs.slide_layouts[5])  # Title only
    slide.shapes.title.text = title

    rows = len(data) + 1  # +1 for header
    cols = len(headers)

    # Default column widths
    if col_widths is None:
        total_width = 11
        col_widths = [total_width / cols] * cols

    # Create table
    table_width = sum(col_widths)
    left = Inches((13.333 - table_width) / 2)  # Center table
    top = Inches(1.8)
    width = Inches(table_width)
    height = Inches(0.5 * rows)

    table = slide.shapes.add_table(rows, cols, left, top, width, height).table

    # Set column widths
    for i, w in enumerate(col_widths):
        table.columns[i].width = Inches(w)

    # Style header row
    for i, header in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = header
        set_cell_color(cell, '2F5496')

        # Format text
        para = cell.text_frame.paragraphs[0]
        para.font.bold = True
        para.font.size = Pt(12)
        para.font.color.rgb = RgbColor(255, 255, 255)
        para.alignment = PP_ALIGN.CENTER
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE

    # Add data rows
    for row_idx, row_data in enumerate(data, start=1):
        for col_idx, value in enumerate(row_data):
            cell = table.cell(row_idx, col_idx)
            cell.text = str(value)

            # Alternate row colors
            if row_idx % 2 == 0:
                set_cell_color(cell, 'D6DCE5')

            # Format text
            para = cell.text_frame.paragraphs[0]
            para.font.size = Pt(11)
            para.alignment = PP_ALIGN.CENTER
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE


def create_table_presentation(output_path: str) -> None:
    """Create presentation with various table examples."""
    prs = Presentation()

    # Simple data table
    headers = ['Product', 'Q1', 'Q2', 'Q3', 'Q4', 'Total']
    data = [
        ['Widget A', '$150K', '$180K', '$220K', '$250K', '$800K'],
        ['Widget B', '$80K', '$95K', '$110K', '$130K', '$415K'],
        ['Widget C', '$200K', '$220K', '$260K', '$290K', '$970K'],
        ['Total', '$430K', '$495K', '$590K', '$670K', '$2.19M'],
    ]

    create_table_slide(
        prs,
        "Quarterly Sales Summary",
        headers,
        data,
        col_widths=[2, 1.5, 1.5, 1.5, 1.5, 1.5]
    )

    # Comparison table
    headers = ['Feature', 'Basic Plan', 'Pro Plan', 'Enterprise']
    data = [
        ['Users', '5', '25', 'Unlimited'],
        ['Storage', '10 GB', '100 GB', '1 TB'],
        ['Support', 'Email', '24/7 Chat', 'Dedicated'],
        ['Price/mo', '$9', '$29', '$99'],
    ]

    create_table_slide(
        prs,
        "Pricing Comparison",
        headers,
        data,
        col_widths=[3, 2.5, 2.5, 2.5]
    )

    # Schedule/Timeline table
    headers = ['Phase', 'Start', 'End', 'Status', 'Owner']
    data = [
        ['Planning', 'Jan 1', 'Jan 15', 'Complete', 'Team A'],
        ['Development', 'Jan 16', 'Mar 31', 'In Progress', 'Team B'],
        ['Testing', 'Apr 1', 'Apr 30', 'Pending', 'Team C'],
        ['Launch', 'May 1', 'May 15', 'Pending', 'Team D'],
    ]

    create_table_slide(
        prs,
        "Project Timeline",
        headers,
        data,
        col_widths=[2.5, 1.5, 1.5, 2, 2]
    )

    prs.save(output_path)
    print(f"Table presentation saved to {output_path}")


create_table_presentation("table_presentation.pptx")
```
