---
name: python-docx-2-advanced-paragraph-formatting
description: 'Sub-skill of python-docx: 2. Advanced Paragraph Formatting.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 2. Advanced Paragraph Formatting

## 2. Advanced Paragraph Formatting


```python
"""
Advanced paragraph formatting with custom styles, spacing, and indentation.
"""
from docx import Document
from docx.shared import Pt, Inches, Cm, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml

def create_formatted_document(output_path: str) -> None:
    """Create document with advanced paragraph formatting."""
    doc = Document()

    # Create custom style
    styles = doc.styles

    # Create paragraph style
    custom_style = styles.add_style('CustomBody', WD_STYLE_TYPE.PARAGRAPH)
    custom_style.font.name = 'Calibri'
    custom_style.font.size = Pt(11)
    custom_style.paragraph_format.space_before = Pt(6)
    custom_style.paragraph_format.space_after = Pt(6)
    custom_style.paragraph_format.line_spacing = 1.15

    # Create character style for highlighting
    highlight_style = styles.add_style('Highlight', WD_STYLE_TYPE.CHARACTER)
    highlight_style.font.bold = True
    highlight_style.font.color.rgb = None  # Will use theme color

    # Add heading
    doc.add_heading('Document Formatting Examples', level=0)

    # Paragraph with custom alignment and spacing
    doc.add_heading('Text Alignment', level=1)

    # Left aligned (default)
    para_left = doc.add_paragraph('Left aligned text (default)')
    para_left.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # Center aligned
    para_center = doc.add_paragraph('Center aligned text')
    para_center.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Right aligned
    para_right = doc.add_paragraph('Right aligned text')
    para_right.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # Justified
    para_justified = doc.add_paragraph(
        'Justified text spreads evenly across the line width. '
        'This is useful for formal documents and reports where '
        'a clean, professional appearance is desired.'
    )
    para_justified.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Line spacing examples
    doc.add_heading('Line Spacing', level=1)

    # Single spacing
    single_para = doc.add_paragraph(
        'Single spaced paragraph. Line spacing is set to 1.0 '
        'which means the lines are close together.'
    )
    single_para.paragraph_format.line_spacing = 1.0

    # 1.5 spacing
    one_half_para = doc.add_paragraph(
        'One and a half spaced paragraph. Line spacing is set to 1.5 '
        'which provides moderate spacing between lines.'
    )
    one_half_para.paragraph_format.line_spacing = 1.5

    # Double spacing
    double_para = doc.add_paragraph(
        'Double spaced paragraph. Line spacing is set to 2.0 '
        'which is common for academic and legal documents.'
    )
    double_para.paragraph_format.line_spacing = 2.0

    # Indentation examples
    doc.add_heading('Indentation', level=1)

    # First line indent
    first_indent = doc.add_paragraph(
        'This paragraph has a first line indent. The first line starts '
        'further to the right than subsequent lines, which is a common '
        'style for body text in books and formal documents.'
    )
    first_indent.paragraph_format.first_line_indent = Inches(0.5)

    # Left indent (block indent)
    left_indent = doc.add_paragraph(
        'This paragraph has a left indent applied. The entire paragraph '
        'is shifted to the right, which is useful for quotations or '
        'secondary information.'
    )
    left_indent.paragraph_format.left_indent = Inches(0.75)

    # Right indent
    right_indent = doc.add_paragraph(
        'This paragraph has a right indent. The right edge of the text '
        'is moved inward from the page margin.'
    )
    right_indent.paragraph_format.right_indent = Inches(0.75)

    # Hanging indent (for references/bibliography)
    hanging = doc.add_paragraph(
        'Smith, J. (2026). The Complete Guide to Document Automation. '
        'Publisher Name. This is an example of a hanging indent commonly '
        'used in bibliographies and reference lists.'
    )
    hanging.paragraph_format.left_indent = Inches(0.5)
    hanging.paragraph_format.first_line_indent = Inches(-0.5)

    # Font formatting examples
    doc.add_heading('Font Formatting', level=1)

    font_para = doc.add_paragraph()

    # Normal text
    font_para.add_run('Normal text, ')

    # Bold
    bold_run = font_para.add_run('bold text, ')
    bold_run.bold = True

    # Italic
    italic_run = font_para.add_run('italic text, ')
    italic_run.italic = True

    # Underline
    underline_run = font_para.add_run('underlined text, ')
    underline_run.underline = True

    # Strikethrough
    strike_run = font_para.add_run('strikethrough text, ')
    strike_run.font.strike = True

    # Subscript
    font_para.add_run('H')
    sub_run = font_para.add_run('2')
    sub_run.font.subscript = True
    font_para.add_run('O, ')

    # Superscript
    font_para.add_run('E=mc')
    sup_run = font_para.add_run('2')
    sup_run.font.superscript = True

    # Different font sizes
    doc.add_heading('Font Sizes', level=2)

    sizes_para = doc.add_paragraph()
    for size in [8, 10, 12, 14, 16, 18, 24]:
        run = sizes_para.add_run(f'{size}pt ')
        run.font.size = Pt(size)

    # Save document
    doc.save(output_path)
    print(f"Formatted document saved to {output_path}")


create_formatted_document('formatted_document.docx')
```
