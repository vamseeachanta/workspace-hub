---
name: python-pptx-2-advanced-text-formatting
description: 'Sub-skill of python-pptx: 2. Advanced Text Formatting.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 2. Advanced Text Formatting

## 2. Advanced Text Formatting


```python
"""
Advanced text formatting with runs, fonts, and paragraph styles.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RgbColor
from pptx.oxml.ns import nsmap

def create_formatted_presentation(output_path: str) -> None:
    """Create presentation with advanced text formatting."""
    prs = Presentation()

    # Slide with formatted text
    slide_layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(slide_layout)

    # Title with formatting
    title_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(0.3),
        Inches(12), Inches(1)
    )
    tf = title_box.text_frame

    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER

    # Multiple runs with different formatting
    run1 = p.add_run()
    run1.text = "Quarterly "
    run1.font.size = Pt(40)
    run1.font.bold = True
    run1.font.color.rgb = RgbColor(0x2F, 0x54, 0x96)

    run2 = p.add_run()
    run2.text = "Performance"
    run2.font.size = Pt(40)
    run2.font.bold = True
    run2.font.color.rgb = RgbColor(0x70, 0xAD, 0x47)

    run3 = p.add_run()
    run3.text = " Report"
    run3.font.size = Pt(40)
    run3.font.bold = True
    run3.font.color.rgb = RgbColor(0x2F, 0x54, 0x96)

    # Formatted paragraph with various styles
    content_box = slide.shapes.add_textbox(
        Inches(0.75), Inches(1.5),
        Inches(11.5), Inches(5)
    )
    tf = content_box.text_frame
    tf.word_wrap = True

    # Paragraph 1: Bold heading
    p1 = tf.paragraphs[0]
    p1.text = "Executive Summary"
    p1.font.size = Pt(24)
    p1.font.bold = True
    p1.space_after = Pt(12)

    # Paragraph 2: Normal text
    p2 = tf.add_paragraph()
    p2.text = (
        "This quarter demonstrated strong performance across all metrics. "
        "Revenue increased by 15% year-over-year, driven by expansion in "
        "key markets and improved customer retention."
    )
    p2.font.size = Pt(16)
    p2.space_after = Pt(18)
    p2.line_spacing = 1.5

    # Paragraph 3: Highlighted text
    p3 = tf.add_paragraph()
    p3.text = "Key Achievement: "
    p3.font.size = Pt(18)
    p3.font.bold = True
    p3.font.color.rgb = RgbColor(0xC0, 0x00, 0x00)

    run = p3.add_run()
    run.text = "Achieved 120% of quarterly target"
    run.font.size = Pt(18)
    run.font.italic = True

    # Paragraph 4: Subscript and superscript
    p4 = tf.add_paragraph()
    p4.space_before = Pt(18)

    run = p4.add_run()
    run.text = "Formula example: H"
    run.font.size = Pt(16)

    sub = p4.add_run()
    sub.text = "2"
    sub.font.size = Pt(12)
    sub.font._element.set(
        '{http://schemas.openxmlformats.org/drawingml/2006/main}baseline', '-25000'
    )

    run = p4.add_run()
    run.text = "O and E=mc"
    run.font.size = Pt(16)

    sup = p4.add_run()
    sup.text = "2"
    sup.font.size = Pt(12)
    sup.font._element.set(
        '{http://schemas.openxmlformats.org/drawingml/2006/main}baseline', '30000'
    )

    # Bullet list with custom formatting
    bullet_box = slide.shapes.add_textbox(
        Inches(0.75), Inches(5),
        Inches(11.5), Inches(2)
    )
    tf = bullet_box.text_frame

    p = tf.paragraphs[0]
    p.text = "Key Metrics:"
    p.font.size = Pt(18)
    p.font.bold = True

    bullets = [
        ("Revenue", "$12.5M", "up 15%"),
        ("Customers", "45,000", "up 8%"),
        ("NPS Score", "72", "up 5 points"),
    ]

    for metric, value, change in bullets:
        p = tf.add_paragraph()
        p.level = 0

        run = p.add_run()
        run.text = f"{metric}: "
        run.font.size = Pt(14)
        run.font.bold = True

        run = p.add_run()
        run.text = f"{value} "
        run.font.size = Pt(14)

        run = p.add_run()
        run.text = f"({change})"
        run.font.size = Pt(14)
        run.font.color.rgb = RgbColor(0x00, 0x80, 0x00)

    prs.save(output_path)
    print(f"Formatted presentation saved to {output_path}")


create_formatted_presentation("formatted_presentation.pptx")
```
