---
name: python-docx-4-headers-footers-and-page-setup
description: 'Sub-skill of python-docx: 4. Headers, Footers, and Page Setup.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 4. Headers, Footers, and Page Setup

## 4. Headers, Footers, and Page Setup


```python
"""
Configure headers, footers, page numbers, and page setup.
"""
from docx import Document
from docx.shared import Inches, Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def add_page_number(paragraph) -> None:
    """Add page number field to paragraph."""
    run = paragraph.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')

    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = "PAGE"

    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')

    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')

    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)


def add_total_pages(paragraph) -> None:
    """Add total page count field to paragraph."""
    run = paragraph.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')

    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = "NUMPAGES"

    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')

    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')

    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)


def create_document_with_headers_footers(output_path: str) -> None:
    """Create document with headers, footers, and page numbers."""
    doc = Document()

    # Access the default section
    section = doc.sections[0]

    # Set page margins
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1.25)
    section.right_margin = Inches(1.25)

    # Set page size (Letter)
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)

    # Configure header
    header = section.header
    header_para = header.paragraphs[0]

    # Add company logo placeholder and title
    header_para.text = "ACME Corporation"
    header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header_run = header_para.runs[0]
    header_run.bold = True
    header_run.font.size = Pt(14)

    # Add subtitle to header
    subtitle_para = header.add_paragraph()
    subtitle_para.text = "Confidential Document"
    subtitle_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle_para.runs[0].font.size = Pt(10)
    subtitle_para.runs[0].italic = True

    # Configure footer with page numbers
    footer = section.footer
    footer_para = footer.paragraphs[0]
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Add "Page X of Y" format
    footer_para.add_run("Page ")
    add_page_number(footer_para)
    footer_para.add_run(" of ")
    add_total_pages(footer_para)

    # Add document content
    doc.add_heading('Document Title', level=0)

    # Add multiple paragraphs to create multiple pages
    for i in range(1, 4):
        doc.add_heading(f'Section {i}', level=1)
        for j in range(5):
            doc.add_paragraph(
                f'This is paragraph {j+1} of section {i}. '
                'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '
                'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '
                'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.'
            )

        # Add page break after each section (except last)
        if i < 3:
            doc.add_page_break()

    doc.save(output_path)
    print(f"Document with headers/footers saved to {output_path}")


def create_landscape_document(output_path: str) -> None:
    """Create document with landscape orientation."""
    doc = Document()

    section = doc.sections[0]

    # Set landscape orientation
    section.orientation = WD_ORIENT.LANDSCAPE

    # Swap width and height for landscape
    new_width = section.page_height
    new_height = section.page_width
    section.page_width = new_width
    section.page_height = new_height

    # Add content
    doc.add_heading('Wide Format Report', level=0)
    doc.add_paragraph('This document is in landscape orientation, ideal for wide tables.')

    # Add wide table
    table = doc.add_table(rows=5, cols=8)
    table.style = 'Table Grid'

    headers = ['ID', 'Name', 'Q1', 'Q2', 'Q3', 'Q4', 'Total', 'Growth']
    for i, header in enumerate(headers):
        table.rows[0].cells[i].text = header

    doc.save(output_path)
    print(f"Landscape document saved to {output_path}")


create_document_with_headers_footers('headers_footers.docx')
create_landscape_document('landscape_report.docx')
```
