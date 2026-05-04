---
name: python-pptx-6-template-based-generation
description: 'Sub-skill of python-pptx: 6. Template-Based Generation.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 6. Template-Based Generation

## 6. Template-Based Generation


```python
"""
Generate presentations from templates with placeholder replacement.
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE_TYPE
from typing import Dict, Any, List
from pathlib import Path
from copy import deepcopy

def replace_text_in_shapes(slide, replacements: Dict[str, str]) -> None:
    """Replace placeholder text in all shapes on a slide."""
    for shape in slide.shapes:
        if shape.has_text_frame:
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    for key, value in replacements.items():
                        if f'{{{{{key}}}}}' in run.text:
                            run.text = run.text.replace(f'{{{{{key}}}}}', str(value))

        if shape.has_table:
            for row in shape.table.rows:
                for cell in row.cells:
                    for paragraph in cell.text_frame.paragraphs:
                        for run in paragraph.runs:
                            for key, value in replacements.items():
                                if f'{{{{{key}}}}}' in run.text:
                                    run.text = run.text.replace(
                                        f'{{{{{key}}}}}',
                                        str(value)
                                    )


def generate_from_template(
    template_path: str,
    output_path: str,
    data: Dict[str, Any]
) -> None:
    """Generate presentation from template with data substitution."""
    prs = Presentation(template_path)

    for slide in prs.slides:
        replace_text_in_shapes(slide, data)

    prs.save(output_path)
    print(f"Generated presentation: {output_path}")


def create_monthly_report_template(output_path: str) -> None:
    """Create a template for monthly reports."""
    prs = Presentation()

    # Title slide with placeholders
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Title placeholder
    title = slide.shapes.add_textbox(
        Inches(0.5), Inches(2.5),
        Inches(12), Inches(1.5)
    )
    tf = title.text_frame
    p = tf.paragraphs[0]
    p.text = "{{report_title}}"
    p.font.size = Pt(44)
    p.font.bold = True
    p.alignment = 1  # Center

    # Subtitle
    subtitle = slide.shapes.add_textbox(
        Inches(0.5), Inches(4),
        Inches(12), Inches(1)
    )
    tf = subtitle.text_frame
    p = tf.paragraphs[0]
    p.text = "{{report_period}}"
    p.font.size = Pt(24)
    p.alignment = 1

    # Summary slide
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    title = slide.shapes.add_textbox(
        Inches(0.5), Inches(0.5),
        Inches(12), Inches(1)
    )
    tf = title.text_frame
    p = tf.paragraphs[0]
    p.text = "Executive Summary"
    p.font.size = Pt(32)
    p.font.bold = True

    # Key metrics boxes
    metrics = [
        ("Revenue", "{{revenue}}"),
        ("Customers", "{{customers}}"),
        ("Growth", "{{growth}}"),
    ]

    for i, (label, placeholder) in enumerate(metrics):
        x = 1 + (i * 4)

        # Label
        label_box = slide.shapes.add_textbox(
            Inches(x), Inches(2),
            Inches(3), Inches(0.5)
        )
        tf = label_box.text_frame
        p = tf.paragraphs[0]
        p.text = label
        p.font.size = Pt(14)
        p.alignment = 1

        # Value box
        shape = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(x), Inches(2.5),
            Inches(3), Inches(1.5)
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = RgbColor(0x44, 0x72, 0xC4)
        tf = shape.text_frame
        p = tf.paragraphs[0]
        p.text = placeholder
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = RgbColor(255, 255, 255)
        p.alignment = 1

    prs.save(output_path)
    print(f"Template saved: {output_path}")


def batch_generate_presentations(
    template_path: str,
    data_list: List[Dict[str, Any]],
    output_dir: str
) -> List[str]:
    """Generate multiple presentations from template."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    generated = []

    for data in data_list:
        filename = f"{data.get('filename', 'presentation')}.pptx"
        file_path = output_path / filename

        generate_from_template(template_path, str(file_path), data)
        generated.append(str(file_path))

    return generated


# Example usage:
# create_monthly_report_template('monthly_template.pptx')
#
# data = {
#     'report_title': 'Monthly Performance Report',
#     'report_period': 'January 2026',
#     'revenue': '$12.5M',
#     'customers': '45,000',
#     'growth': '+15%'
# }
# generate_from_template('monthly_template.pptx', 'january_report.pptx', data)
```
