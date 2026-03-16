---
name: theme-factory-htmlcss
description: 'Sub-skill of theme-factory: HTML/CSS (+2).'
version: 2.0.0
category: business
type: reference
scripts_exempt: true
---

# HTML/CSS (+2)

## HTML/CSS


```html
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono&display=swap" rel="stylesheet">

<style>
  :root {
    --primary: #0d0221;
    --secondary: #1a0533;
    --accent: #7c3aed;
    --highlight: #a78bfa;
    --text: #f5f3ff;

*See sub-skills for full details.*

## PowerPoint (python-pptx)


```python
from pptx.dml.color import RGBColor

# Tech Innovation theme
THEME = {
    'primary': RGBColor(0x0d, 0x02, 0x21),
    'secondary': RGBColor(0x1a, 0x05, 0x33),
    'accent': RGBColor(0x7c, 0x3a, 0xed),
    'highlight': RGBColor(0xa7, 0x8b, 0xfa),
    'text': RGBColor(0xf5, 0xf3, 0xff),

*See sub-skills for full details.*

## Excel (openpyxl)


```python
from openpyxl.styles import PatternFill, Font

# Tech Innovation theme
header_fill = PatternFill(start_color="7c3aed", fill_type="solid")
header_font = Font(name="Space Grotesk", color="f5f3ff", bold=True)

# Apply to cells
for cell in ws[1]:
    cell.fill = header_fill
    cell.font = header_font
```
