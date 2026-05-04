---
name: pptx-before-writing-code
description: 'Sub-skill of pptx: Before Writing Code (+1).'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Before Writing Code (+1)

## Before Writing Code


State your content-informed design approach:
1. What is the purpose and tone?
2. Select colors that genuinely match the topic
3. Plan visual hierarchy and layout
4. Consider typography choices

## Professional Styling


```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])

# Add styled text box

*See sub-skills for full details.*
