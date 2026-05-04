---
name: python-docx-6-style-management-and-custom-styles
description: 'Sub-skill of python-docx: 6. Style Management and Custom Styles.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 6. Style Management and Custom Styles

## 6. Style Management and Custom Styles


```python
"""
Create and manage document styles for consistent formatting.
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from typing import Dict, Any

def create_custom_styles(doc: Document) -> Dict[str, Any]:
    """Create a set of custom styles for the document."""
    styles = doc.styles
    created_styles = {}

    # Custom Heading 1
    if 'CustomHeading1' not in [s.name for s in styles]:
        h1_style = styles.add_style('CustomHeading1', WD_STYLE_TYPE.PARAGRAPH)
        h1_style.base_style = styles['Heading 1']
        h1_style.font.name = 'Georgia'
        h1_style.font.size = Pt(18)
        h1_style.font.bold = True
        h1_style.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)
        h1_style.paragraph_format.space_before = Pt(24)
        h1_style.paragraph_format.space_after = Pt(12)
        created_styles['heading1'] = h1_style

    # Custom Heading 2
    if 'CustomHeading2' not in [s.name for s in styles]:
        h2_style = styles.add_style('CustomHeading2', WD_STYLE_TYPE.PARAGRAPH)
        h2_style.base_style = styles['Heading 2']
        h2_style.font.name = 'Georgia'
        h2_style.font.size = Pt(14)
        h2_style.font.bold = True
        h2_style.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)
        h2_style.paragraph_format.space_before = Pt(18)
        h2_style.paragraph_format.space_after = Pt(6)
        created_styles['heading2'] = h2_style

    # Custom Body Text
    if 'CustomBody' not in [s.name for s in styles]:
        body_style = styles.add_style('CustomBody', WD_STYLE_TYPE.PARAGRAPH)
        body_style.font.name = 'Calibri'
        body_style.font.size = Pt(11)
        body_style.paragraph_format.space_after = Pt(8)
        body_style.paragraph_format.line_spacing = 1.15
        body_style.paragraph_format.first_line_indent = Inches(0.25)
        created_styles['body'] = body_style

    # Custom Quote
    if 'CustomQuote' not in [s.name for s in styles]:
        quote_style = styles.add_style('CustomQuote', WD_STYLE_TYPE.PARAGRAPH)
        quote_style.font.name = 'Calibri'
        quote_style.font.size = Pt(11)
        quote_style.font.italic = True
        quote_style.font.color.rgb = RGBColor(0x59, 0x59, 0x59)
        quote_style.paragraph_format.left_indent = Inches(0.5)
        quote_style.paragraph_format.right_indent = Inches(0.5)
        quote_style.paragraph_format.space_before = Pt(12)
        quote_style.paragraph_format.space_after = Pt(12)
        created_styles['quote'] = quote_style

    # Code Block Style
    if 'CodeBlock' not in [s.name for s in styles]:
        code_style = styles.add_style('CodeBlock', WD_STYLE_TYPE.PARAGRAPH)
        code_style.font.name = 'Consolas'
        code_style.font.size = Pt(10)
        code_style.paragraph_format.space_before = Pt(6)
        code_style.paragraph_format.space_after = Pt(6)
        code_style.paragraph_format.left_indent = Inches(0.25)
        created_styles['code'] = code_style

    # Highlight Character Style
    if 'Highlight' not in [s.name for s in styles]:
        highlight_style = styles.add_style('Highlight', WD_STYLE_TYPE.CHARACTER)
        highlight_style.font.bold = True
        highlight_style.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
        created_styles['highlight'] = highlight_style

    return created_styles


def create_styled_document(output_path: str) -> None:
    """Create document using custom styles."""
    doc = Document()

    # Create custom styles
    create_custom_styles(doc)

    # Use custom styles
    doc.add_paragraph('Technical Report', style='CustomHeading1')

    doc.add_paragraph('Introduction', style='CustomHeading2')

    intro = doc.add_paragraph(
        'This document demonstrates the use of custom styles for consistent '
        'formatting throughout the document. Custom styles allow you to define '
        'formatting once and apply it consistently.',
        style='CustomBody'
    )

    doc.add_paragraph('Key Concepts', style='CustomHeading2')

    doc.add_paragraph(
        'Style management is essential for professional documents. '
        'It ensures consistency and makes global formatting changes easy.',
        style='CustomBody'
    )

    # Add quote
    doc.add_paragraph(
        '"Good typography is invisible. Bad typography is everywhere." - Oliver Reichenstein',
        style='CustomQuote'
    )

    doc.add_paragraph('Code Example', style='CustomHeading2')

    # Add code block
    code = """def hello_world():
    print("Hello, World!")
    return True"""

    doc.add_paragraph(code, style='CodeBlock')

    doc.add_paragraph('Conclusion', style='CustomHeading2')

    conclusion = doc.add_paragraph(style='CustomBody')
    conclusion.add_run('Custom styles provide ')
    highlight_run = conclusion.add_run('powerful formatting control')
    highlight_run.style = 'Highlight'
    conclusion.add_run(' for document automation.')

    doc.save(output_path)
    print(f"Styled document saved to {output_path}")


create_styled_document('styled_document.docx')
```
