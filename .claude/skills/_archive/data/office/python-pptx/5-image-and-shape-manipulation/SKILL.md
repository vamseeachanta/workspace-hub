---
name: python-pptx-5-image-and-shape-manipulation
description: 'Sub-skill of python-pptx: 5. Image and Shape Manipulation.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 5. Image and Shape Manipulation

## 5. Image and Shape Manipulation


```python
"""
Add and manipulate images and shapes in presentations.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RgbColor
from pathlib import Path
from io import BytesIO
from typing import Tuple

def add_image_with_border(
    slide,
    image_path: str,
    left: float,
    top: float,
    width: float = None,
    height: float = None
) -> None:
    """Add image with optional border effect."""
    if Path(image_path).exists():
        pic = slide.shapes.add_picture(
            image_path,
            Inches(left), Inches(top),
            Inches(width) if width else None,
            Inches(height) if height else None
        )
        # Add line border
        pic.line.color.rgb = RgbColor(0, 0, 0)
        pic.line.width = Pt(1)


def create_arrow_connector(
    slide,
    start: Tuple[float, float],
    end: Tuple[float, float],
    color: str = "4472C4"
) -> None:
    """Create an arrow connector between two points."""
    connector = slide.shapes.add_connector(
        MSO_CONNECTOR.STRAIGHT,
        Inches(start[0]), Inches(start[1]),
        Inches(end[0]), Inches(end[1])
    )

    connector.line.color.rgb = RgbColor(
        int(color[0:2], 16),
        int(color[2:4], 16),
        int(color[4:6], 16)
    )
    connector.line.width = Pt(2)


def create_shape_presentation(output_path: str) -> None:
    """Create presentation with shapes and connectors."""
    prs = Presentation()

    # Slide 1: Process Flow with Shapes
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank

    # Add title
    title_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(0.3),
        Inches(12), Inches(0.8)
    )
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "Development Process Flow"
    p.font.size = Pt(32)
    p.font.bold = True
    p.alignment = PP_ALIGN.CENTER

    # Process steps
    steps = [
        ("Requirements", "4472C4"),
        ("Design", "70AD47"),
        ("Development", "ED7D31"),
        ("Testing", "5B9BD5"),
        ("Deployment", "7030A0"),
    ]

    y_pos = 2.5
    x_positions = [1, 3.5, 6, 8.5, 11]

    for i, (step, color) in enumerate(steps):
        # Add shape
        shape = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(x_positions[i]), Inches(y_pos),
            Inches(2), Inches(1)
        )

        shape.fill.solid()
        shape.fill.fore_color.rgb = RgbColor(
            int(color[0:2], 16),
            int(color[2:4], 16),
            int(color[4:6], 16)
        )

        # Add text
        tf = shape.text_frame
        p = tf.paragraphs[0]
        p.text = step
        p.font.color.rgb = RgbColor(255, 255, 255)
        p.font.bold = True
        p.font.size = Pt(14)
        p.alignment = PP_ALIGN.CENTER
        shape.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

        # Add arrow to next step
        if i < len(steps) - 1:
            arrow = slide.shapes.add_shape(
                MSO_SHAPE.RIGHT_ARROW,
                Inches(x_positions[i] + 2.1), Inches(y_pos + 0.35),
                Inches(0.3), Inches(0.3)
            )
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = RgbColor(128, 128, 128)

    # Slide 2: Organization Chart Style
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    title_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(0.3),
        Inches(12), Inches(0.8)
    )
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "Team Structure"
    p.font.size = Pt(32)
    p.font.bold = True
    p.alignment = PP_ALIGN.CENTER

    # CEO box
    ceo = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(5.5), Inches(1.5),
        Inches(2.5), Inches(1)
    )
    ceo.fill.solid()
    ceo.fill.fore_color.rgb = RgbColor(0x2F, 0x54, 0x96)
    ceo.text = "CEO\nJohn Smith"
    for para in ceo.text_frame.paragraphs:
        para.font.color.rgb = RgbColor(255, 255, 255)
        para.font.size = Pt(12)
        para.alignment = PP_ALIGN.CENTER

    # Department heads
    departments = [
        ("Engineering\nAlice Chen", 1.5),
        ("Marketing\nBob Wilson", 4.5),
        ("Sales\nCarol Davis", 7.5),
        ("Operations\nDave Brown", 10.5),
    ]

    for name, x_pos in departments:
        box = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(x_pos), Inches(3.5),
            Inches(2.5), Inches(1)
        )
        box.fill.solid()
        box.fill.fore_color.rgb = RgbColor(0x5B, 0x9B, 0xD5)
        box.text = name
        for para in box.text_frame.paragraphs:
            para.font.color.rgb = RgbColor(255, 255, 255)
            para.font.size = Pt(11)
            para.alignment = PP_ALIGN.CENTER

    # Slide 3: Callout Shapes
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    title_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(0.3),
        Inches(12), Inches(0.8)
    )
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "Key Callouts"
    p.font.size = Pt(32)
    p.font.bold = True
    p.alignment = PP_ALIGN.CENTER

*Content truncated — see parent skill for full reference.*
