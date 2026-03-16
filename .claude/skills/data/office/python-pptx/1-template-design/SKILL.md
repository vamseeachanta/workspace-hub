---
name: python-pptx-1-template-design
description: 'Sub-skill of python-pptx: 1. Template Design (+2).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Template Design (+2)

## 1. Template Design


```python
"""Best practices for template-based generation."""

# DO: Use consistent placeholder naming
PLACEHOLDERS = {
    'title': '{{title}}',
    'subtitle': '{{subtitle}}',
    'date': '{{date}}',
    'author': '{{author}}'
}

# DO: Create reusable slide builders
class SlideBuilder:
    def __init__(self, prs):
        self.prs = prs

    def add_title_slide(self, title, subtitle):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[0])
        slide.shapes.title.text = title
        if subtitle:
            slide.placeholders[1].text = subtitle
        return slide

    def add_content_slide(self, title, bullets):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[1])
        slide.shapes.title.text = title
        tf = slide.placeholders[1].text_frame
        tf.text = bullets[0]
        for bullet in bullets[1:]:
            p = tf.add_paragraph()
            p.text = bullet
        return slide
```


## 2. Performance Optimization


```python
"""Performance tips for large presentations."""

# DO: Reuse color objects
COLORS = {
    'primary': RgbColor(0x2F, 0x54, 0x96),
    'secondary': RgbColor(0x70, 0xAD, 0x47),
    'accent': RgbColor(0xED, 0x7D, 0x31)
}

# DO: Batch similar operations
def add_multiple_charts(prs, chart_data_list):
    for title, data, chart_type in chart_data_list:
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        slide.shapes.title.text = title
        # Add chart...
```


## 3. Error Handling


```python
"""Robust error handling for presentations."""
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def safe_generate_presentation(template_path, output_path, data):
    """Generate presentation with error handling."""
    try:
        if not Path(template_path).exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        prs = Presentation(template_path)
        # Process...
        prs.save(output_path)

        return {"success": True, "path": output_path}

    except Exception as e:
        logger.exception(f"Presentation generation failed: {e}")
        return {"success": False, "error": str(e)}
```
