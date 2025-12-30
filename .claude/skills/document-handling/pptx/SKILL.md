---
name: pptx
description: PowerPoint presentation toolkit for creating new presentations, editing existing ones, and using templates. Supports HTML-to-PPTX conversion, slide manipulation, and professional design. Use when building presentations, slide decks, or visual reports.
---

# PPTX Processing Skill

## Overview

This skill provides three primary workflows for PowerPoint manipulation: creating from scratch, editing existing presentations, and using templates.

## Creating New Presentations

### Basic Creation with python-pptx
```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

prs = Presentation()

# Add title slide
title_slide_layout = prs.slide_layouts[0]
slide = prs.slides.add_slide(title_slide_layout)
title = slide.shapes.title
subtitle = slide.placeholders[1]

title.text = "Presentation Title"
subtitle.text = "Subtitle or Author"

# Add content slide
bullet_slide_layout = prs.slide_layouts[1]
slide = prs.slides.add_slide(bullet_slide_layout)
shapes = slide.shapes

title_shape = shapes.title
body_shape = shapes.placeholders[1]

title_shape.text = "Slide Title"
tf = body_shape.text_frame
tf.text = "First bullet point"

p = tf.add_paragraph()
p.text = "Second bullet point"
p.level = 0

p = tf.add_paragraph()
p.text = "Sub-bullet"
p.level = 1

prs.save("presentation.pptx")
```

### Add Images
```python
from pptx import Presentation
from pptx.util import Inches

prs = Presentation()
blank_slide_layout = prs.slide_layouts[6]
slide = prs.slides.add_slide(blank_slide_layout)

left = Inches(1)
top = Inches(1)
width = Inches(5)

slide.shapes.add_picture("image.png", left, top, width=width)

prs.save("with_image.pptx")
```

### Add Charts
```python
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])

chart_data = CategoryChartData()
chart_data.categories = ['Q1', 'Q2', 'Q3', 'Q4']
chart_data.add_series('Sales', (19.2, 21.4, 16.7, 28.0))
chart_data.add_series('Expenses', (14.2, 18.3, 15.4, 20.1))

x, y, cx, cy = Inches(2), Inches(2), Inches(6), Inches(4.5)
slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data
)

prs.save("with_chart.pptx")
```

### Add Tables
```python
from pptx import Presentation
from pptx.util import Inches

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])

rows, cols = 3, 4
left = Inches(1)
top = Inches(2)
width = Inches(6)
height = Inches(2)

table = slide.shapes.add_table(rows, cols, left, top, width, height).table

# Set column widths
for col_idx in range(cols):
    table.columns[col_idx].width = Inches(1.5)

# Fill cells
for row_idx, row in enumerate(table.rows):
    for col_idx, cell in enumerate(row.cells):
        cell.text = f"R{row_idx+1}C{col_idx+1}"

prs.save("with_table.pptx")
```

## Design Principles

### Before Writing Code
State your content-informed design approach:
1. What is the purpose and tone?
2. Select colors that genuinely match the topic
3. Plan visual hierarchy and layout
4. Consider typography choices

### Professional Styling
```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])

# Add styled text box
left = Inches(1)
top = Inches(1)
width = Inches(8)
height = Inches(1)

txBox = slide.shapes.add_textbox(left, top, width, height)
tf = txBox.text_frame

p = tf.paragraphs[0]
p.text = "Styled Heading"
p.font.size = Pt(44)
p.font.bold = True
p.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)
p.alignment = PP_ALIGN.CENTER

prs.save("styled.pptx")
```

## Editing Existing Presentations

### Read and Modify
```python
from pptx import Presentation

prs = Presentation("existing.pptx")

for slide in prs.slides:
    for shape in slide.shapes:
        if shape.has_text_frame:
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    if "old text" in run.text:
                        run.text = run.text.replace("old text", "new text")

prs.save("modified.pptx")
```

### Extract Text
```python
from pptx import Presentation

prs = Presentation("presentation.pptx")

for slide_num, slide in enumerate(prs.slides, 1):
    print(f"\n--- Slide {slide_num} ---")
    for shape in slide.shapes:
        if shape.has_text_frame:
            for paragraph in shape.text_frame.paragraphs:
                print(paragraph.text)
```

### Copy Slides
```python
from pptx import Presentation
from copy import deepcopy

prs = Presentation("source.pptx")
# Note: python-pptx doesn't directly support slide copying
# Use slide layouts from the same presentation instead
```

## Using Templates

### Apply Template
```python
from pptx import Presentation

# Open template
prs = Presentation("template.pptx")

# Add slides using template layouts
slide_layout = prs.slide_layouts[1]  # Use template's layout
slide = prs.slides.add_slide(slide_layout)

# Fill placeholders
for shape in slide.placeholders:
    print(f"{shape.placeholder_format.idx}: {shape.name}")

prs.save("from_template.pptx")
```

## OOXML Editing (Advanced)

For complex modifications, work directly with XML:

### Unpack Presentation
```bash
unzip presentation.pptx -d presentation_extracted/
```

### Edit XML
Navigate to `ppt/slides/` and edit `slide1.xml`, etc.

### Repack
```bash
cd presentation_extracted
zip -r ../modified.pptx .
```

## Quick Reference

| Task | Method |
|------|--------|
| Create presentation | Presentation() |
| Add slide | slides.add_slide(layout) |
| Add text | add_textbox() |
| Add image | add_picture() |
| Add chart | add_chart() |
| Add table | add_table() |
| Style text | font.size, font.bold, font.color |

## Dependencies

```bash
pip install python-pptx
```

Optional tools:
- LibreOffice (for PDF conversion)
- Pandoc (for format conversion)

---

## Version History

- **1.0.0** (2024-10-15): Initial release with python-pptx, templates, OOXML editing
