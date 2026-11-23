---
name: pptx-apply-template
description: 'Sub-skill of pptx: Apply Template.'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Apply Template

## Apply Template


```python
from pptx import Presentation

# Open template
prs = Presentation("template.pptx")

# Add slides using template layouts
slide_layout = prs.slide_layouts[1]  # Use template's layout
slide = prs.slides.add_slide(slide_layout)


*See sub-skills for full details.*
