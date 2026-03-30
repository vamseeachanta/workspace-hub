---
name: python-pptx-1-basic-presentation-creation
description: 'Sub-skill of python-pptx: 1. Basic Presentation Creation.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Basic Presentation Creation

## 1. Basic Presentation Creation


```python
"""
Create a basic PowerPoint presentation with common slide types.
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RgbColor
from pptx.enum.shapes import MSO_SHAPE

def create_basic_presentation(output_path: str) -> None:
    """Create a basic presentation with various slide types."""
    # Create presentation
    prs = Presentation()

    # Set slide dimensions (16:9 widescreen)
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Slide 1: Title Slide
    title_layout = prs.slide_layouts[0]  # Title slide layout
    slide1 = prs.slides.add_slide(title_layout)

    title = slide1.shapes.title
    subtitle = slide1.placeholders[1]

    title.text = "Q1 2026 Business Review"
    subtitle.text = "Strategic Planning and Performance Analysis"

    # Format title
    for paragraph in title.text_frame.paragraphs:
        paragraph.font.size = Pt(44)
        paragraph.font.bold = True

    # Slide 2: Title and Content
    bullet_layout = prs.slide_layouts[1]  # Title and content
    slide2 = prs.slides.add_slide(bullet_layout)

    title2 = slide2.shapes.title
    body2 = slide2.placeholders[1]

    title2.text = "Key Highlights"

    tf = body2.text_frame
    tf.text = "Revenue grew 15% year-over-year"

    p1 = tf.add_paragraph()
    p1.text = "Customer satisfaction reached 92%"
    p1.level = 0

    p2 = tf.add_paragraph()
    p2.text = "Expanded to 3 new markets"
    p2.level = 0

    p3 = tf.add_paragraph()
    p3.text = "North America"
    p3.level = 1

    p4 = tf.add_paragraph()
    p4.text = "Europe"
    p4.level = 1

    p5 = tf.add_paragraph()
    p5.text = "Asia Pacific"
    p5.level = 1

    # Slide 3: Two Content Slide
    two_content_layout = prs.slide_layouts[3]  # Two content
    slide3 = prs.slides.add_slide(two_content_layout)

    title3 = slide3.shapes.title
    title3.text = "Comparison Overview"

    # Left content
    left_placeholder = slide3.placeholders[1]
    tf_left = left_placeholder.text_frame
    tf_left.text = "Before"
    p = tf_left.add_paragraph()
    p.text = "Manual processes"
    p = tf_left.add_paragraph()
    p.text = "Limited scalability"
    p = tf_left.add_paragraph()
    p.text = "Higher costs"

    # Right content
    right_placeholder = slide3.placeholders[2]
    tf_right = right_placeholder.text_frame
    tf_right.text = "After"
    p = tf_right.add_paragraph()
    p.text = "Automated workflows"
    p = tf_right.add_paragraph()
    p.text = "Unlimited scale"
    p = tf_right.add_paragraph()
    p.text = "Cost reduction"

    # Slide 4: Section Header
    section_layout = prs.slide_layouts[2]  # Section header
    slide4 = prs.slides.add_slide(section_layout)

    title4 = slide4.shapes.title
    title4.text = "Financial Overview"

    # Slide 5: Blank slide with custom shapes
    blank_layout = prs.slide_layouts[6]  # Blank
    slide5 = prs.slides.add_slide(blank_layout)

    # Add custom text box
    left = Inches(0.5)
    top = Inches(0.5)
    width = Inches(12)
    height = Inches(1)

    textbox = slide5.shapes.add_textbox(left, top, width, height)
    tf = textbox.text_frame
    p = tf.paragraphs[0]
    p.text = "Custom Content Slide"
    p.font.size = Pt(32)
    p.font.bold = True
    p.alignment = PP_ALIGN.CENTER

    # Add shapes
    shapes = slide5.shapes

    # Rectangle
    rect = shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(1), Inches(2),
        Inches(3), Inches(2)
    )
    rect.fill.solid()
    rect.fill.fore_color.rgb = RgbColor(0x44, 0x72, 0xC4)
    rect.text = "Feature A"

    # Rounded rectangle
    rounded = shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(5), Inches(2),
        Inches(3), Inches(2)
    )
    rounded.fill.solid()
    rounded.fill.fore_color.rgb = RgbColor(0x70, 0xAD, 0x47)
    rounded.text = "Feature B"

    # Oval
    oval = shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(9), Inches(2),
        Inches(3), Inches(2)
    )
    oval.fill.solid()
    oval.fill.fore_color.rgb = RgbColor(0xED, 0x7D, 0x31)
    oval.text = "Feature C"

    # Save presentation
    prs.save(output_path)
    print(f"Presentation saved to {output_path}")


create_basic_presentation("basic_presentation.pptx")
```
