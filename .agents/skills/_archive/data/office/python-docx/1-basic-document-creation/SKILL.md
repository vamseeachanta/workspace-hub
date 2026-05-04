---
name: python-docx-1-basic-document-creation
description: 'Sub-skill of python-docx: 1. Basic Document Creation.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Basic Document Creation

## 1. Basic Document Creation


```python
"""
Create a basic Word document with title, paragraphs, and formatting.
"""
from docx import Document
from docx.shared import Inches, Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def create_basic_document(output_path: str) -> None:
    """Create a basic document with common elements."""
    # Create new document
    doc = Document()

    # Set document properties
    core_properties = doc.core_properties
    core_properties.author = "Document Generator"
    core_properties.title = "Sample Report"
    core_properties.subject = "Automated Document Generation"

    # Add title with formatting
    title = doc.add_heading('Monthly Performance Report', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Add subtitle paragraph
    subtitle = doc.add_paragraph()
    subtitle_run = subtitle.add_run('January 2026')
    subtitle_run.font.size = Pt(14)
    subtitle_run.font.italic = True
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Add section heading
    doc.add_heading('Executive Summary', level=1)

    # Add paragraph with multiple runs (different formatting)
    para = doc.add_paragraph()
    para.add_run('This report summarizes ').font.size = Pt(11)
    bold_run = para.add_run('key performance metrics')
    bold_run.bold = True
    bold_run.font.size = Pt(11)
    para.add_run(' for the month of January 2026.')

    # Add bullet points
    doc.add_heading('Key Highlights', level=2)

    bullets = [
        'Revenue increased by 15% compared to last month',
        'Customer satisfaction score reached 92%',
        'New user registrations up 25%',
        'Support ticket resolution time reduced by 10%'
    ]

    for bullet in bullets:
        para = doc.add_paragraph(bullet, style='List Bullet')

    # Add numbered list
    doc.add_heading('Action Items', level=2)

    actions = [
        'Review Q1 budget allocation',
        'Schedule team performance reviews',
        'Finalize marketing campaign for Q2'
    ]

    for action in actions:
        doc.add_paragraph(action, style='List Number')

    # Save document
    doc.save(output_path)
    print(f"Document saved to {output_path}")


# Usage
create_basic_document('basic_report.docx')
```
