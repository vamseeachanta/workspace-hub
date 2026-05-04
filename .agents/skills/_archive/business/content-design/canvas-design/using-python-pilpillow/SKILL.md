---
name: canvas-design-using-python-pilpillow
description: 'Sub-skill of canvas-design: Using Python (PIL/Pillow) (+2).'
version: 2.0.0
category: business
type: reference
scripts_exempt: true
---

# Using Python (PIL/Pillow) (+2)

## Using Python (PIL/Pillow)


```python
from PIL import Image, ImageDraw, ImageFont
import math

# Create canvas
width, height = 2400, 3200
canvas = Image.new('RGB', (width, height), '#0a0a0a')
draw = ImageDraw.Draw(canvas)

# Geometric composition

*See sub-skills for full details.*

## Using Cairo (Vector Graphics)


```python
import cairo
import math

width, height = 2400, 3200
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
ctx = cairo.Context(surface)

# Background
ctx.set_source_rgb(0.04, 0.04, 0.04)

*See sub-skills for full details.*

## Using SVG (for PDF conversion)


```python
import svgwrite

dwg = svgwrite.Drawing('composition.svg', size=('24in', '32in'))

# Background
dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='#0a0a0a'))

# Geometric elements
for i in range(20):

*See sub-skills for full details.*
