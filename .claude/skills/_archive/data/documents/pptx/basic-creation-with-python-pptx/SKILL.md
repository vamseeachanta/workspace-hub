---
name: pptx-basic-creation-with-python-pptx
description: 'Sub-skill of pptx: Basic Creation with python-pptx (+3).'
version: 1.1.0
category: data
type: reference
scripts_exempt: true
---

# Basic Creation with python-pptx (+3)

## Basic Creation with python-pptx


```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

prs = Presentation()

# Add title slide
title_slide_layout = prs.slide_layouts[0]
slide = prs.slides.add_slide(title_slide_layout)

*See sub-skills for full details.*

## Add Images


```python
from pptx import Presentation
from pptx.util import Inches

prs = Presentation()
blank_slide_layout = prs.slide_layouts[6]
slide = prs.slides.add_slide(blank_slide_layout)

left = Inches(1)
top = Inches(1)

*See sub-skills for full details.*

## Add Charts


```python
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])

chart_data = CategoryChartData()

*See sub-skills for full details.*

## Add Tables


```python
from pptx import Presentation
from pptx.util import Inches

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])

rows, cols = 3, 4
left = Inches(1)
top = Inches(2)

*See sub-skills for full details.*
