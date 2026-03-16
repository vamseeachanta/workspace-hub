---
name: python-docx-3-table-creation-and-formatting
description: 'Sub-skill of python-docx: 3. Table Creation and Formatting.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 3. Table Creation and Formatting

## 3. Table Creation and Formatting


```python
"""
Create and format tables with merged cells, styles, and custom formatting.
"""
from docx import Document
from docx.shared import Inches, Pt, Cm, Twips
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ROW_HEIGHT_RULE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import nsdecls, qn
from docx.oxml import parse_xml, OxmlElement
from typing import List, Dict, Any, Optional

def set_cell_shading(cell, color: str) -> None:
    """Set cell background color."""
    shading_elm = OxmlElement('w:shd')
    shading_elm.set(qn('w:fill'), color)
    cell._tc.get_or_add_tcPr().append(shading_elm)


def set_cell_borders(cell, border_color: str = "000000", border_size: int = 4) -> None:
    """Set cell borders."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')

    for border_name in ['top', 'left', 'bottom', 'right']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), str(border_size))
        border.set(qn('w:color'), border_color)
        tcBorders.append(border)

    tcPr.append(tcBorders)


def create_data_table(
    doc: Document,
    headers: List[str],
    data: List[List[Any]],
    header_color: str = "4472C4",
    alternate_row_color: Optional[str] = "D9E2F3"
) -> None:
    """Create a formatted data table with headers and styling."""
    # Create table
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Style header row
    header_cells = table.rows[0].cells
    for i, header in enumerate(headers):
        cell = header_cells[i]
        cell.text = header

        # Format header cell
        set_cell_shading(cell, header_color)

        # Format text
        paragraph = cell.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.runs[0]
        run.font.bold = True
        run.font.color.rgb = None  # White text
        run.font.size = Pt(11)

    # Add data rows
    for row_idx, row_data in enumerate(data):
        row = table.add_row()

        for col_idx, value in enumerate(row_data):
            cell = row.cells[col_idx]
            cell.text = str(value)

            # Alternate row shading
            if alternate_row_color and row_idx % 2 == 0:
                set_cell_shading(cell, alternate_row_color)

            # Center align numbers
            if isinstance(value, (int, float)):
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    return table


def create_merged_header_table(doc: Document) -> None:
    """Create table with merged cells for complex headers."""
    # Create 5x4 table
    table = doc.add_table(rows=5, cols=4)
    table.style = 'Table Grid'

    # Merge cells for main header
    top_left = table.cell(0, 0)
    top_right = table.cell(0, 3)
    top_left.merge(top_right)
    top_left.text = "Quarterly Sales Report 2026"
    top_left.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    top_left.paragraphs[0].runs[0].bold = True
    set_cell_shading(top_left, "2F5496")

    # Merge cells for category headers
    # Q1-Q2 header
    q1_q2 = table.cell(1, 1)
    q1_q2_end = table.cell(1, 2)
    q1_q2.merge(q1_q2_end)
    q1_q2.text = "First Half"
    q1_q2.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_cell_shading(q1_q2, "5B9BD5")

    # Q3-Q4 header
    table.cell(1, 3).text = "Q3-Q4"
    set_cell_shading(table.cell(1, 3), "5B9BD5")

    # Product header (merged vertically)
    table.cell(1, 0).text = "Product"
    set_cell_shading(table.cell(1, 0), "5B9BD5")

    # Sub-headers
    sub_headers = ['', 'Q1', 'Q2', 'Total']
    for i, header in enumerate(sub_headers):
        cell = table.cell(2, i)
        cell.text = header
        set_cell_shading(cell, "BDD7EE")

    # Data rows
    data = [
        ['Widget A', '100', '150', '250'],
        ['Widget B', '200', '180', '380']
    ]

    for row_idx, row_data in enumerate(data, start=3):
        for col_idx, value in enumerate(row_data):
            table.cell(row_idx, col_idx).text = value


def create_document_with_tables(output_path: str) -> None:
    """Create document with various table examples."""
    doc = Document()

    doc.add_heading('Table Examples', level=0)

    # Simple data table
    doc.add_heading('Sales Data', level=1)

    headers = ['Product', 'Q1 Sales', 'Q2 Sales', 'Q3 Sales', 'Q4 Sales', 'Total']
    data = [
        ['Laptop Pro', 150, 175, 200, 225, 750],
        ['Desktop Ultra', 80, 95, 110, 130, 415],
        ['Monitor HD', 200, 220, 240, 260, 920],
        ['Keyboard Elite', 500, 520, 540, 580, 2140],
    ]

    create_data_table(doc, headers, data)

    doc.add_paragraph()  # Spacing

    # Merged header table
    doc.add_heading('Complex Table with Merged Cells', level=1)
    create_merged_header_table(doc)

    doc.add_paragraph()

    # Table with specific column widths
    doc.add_heading('Table with Custom Column Widths', level=1)

    table = doc.add_table(rows=4, cols=3)
    table.style = 'Table Grid'

    # Set column widths
    widths = [Inches(1.5), Inches(3.0), Inches(1.5)]
    for row in table.rows:
        for idx, (cell, width) in enumerate(zip(row.cells, widths)):
            cell.width = width

    # Add content
    headers = ['ID', 'Description', 'Status']
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        cell.paragraphs[0].runs[0].bold = True
        set_cell_shading(cell, "E7E6E6")

    data = [
        ['001', 'Implement new feature for document generation', 'Complete'],
        ['002', 'Review and approve design specifications', 'In Progress'],
        ['003', 'Deploy to production environment', 'Pending'],

*Content truncated — see parent skill for full reference.*
