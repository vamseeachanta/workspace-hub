---
name: canvas-design
description: Create original visual art in PNG and PDF formats using design philosophy principles. Express aesthetic movements visually with minimal text. Use for creating museum-quality visual artifacts, design manifestos, and artistic compositions.
version: 2.0.0
category: content-design
last_updated: 2026-01-02
related_skills:
  - algorithmic-art
  - frontend-design
  - theme-factory
---

# Canvas Design Skill

## Overview

This skill guides creation of original visual art in PNG and PDF formats using design philosophy principles. Emphasize craftsmanship and express aesthetic movements visually rather than through text.

## When to Use

- Creating museum-quality visual artifacts
- Generating design manifestos with visual expression
- Building artistic compositions for presentations or publications
- Producing abstract art for branding or decoration
- Any project requiring 90%+ visual design with minimal text

## Quick Start

1. **Write design philosophy** (4-6 paragraphs articulating visual essence)
2. **Choose visual style** (geometric, organic, structured chaos, typographic)
3. **Select implementation** (PIL/Pillow, Cairo, SVG)
4. **Execute with precision** (museum-quality craftsmanship)
5. **Export** (PNG at 300 DPI or vector PDF)

```python
# Quick geometric composition
from PIL import Image, ImageDraw
import math

canvas = Image.new('RGB', (2400, 3200), '#0a0a0a')
draw = ImageDraw.Draw(canvas)

# Golden ratio spiral
phi = (1 + math.sqrt(5)) / 2
center_x, center_y = 1200, 1600
for i in range(50):
    angle = i * phi * 2 * math.pi
    radius = i * 8
    x = center_x + radius * math.cos(angle)
    y = center_y + radius * math.sin(angle)
    size = max(2, 20 - i * 0.3)
    draw.ellipse([x-size, y-size, x+size, y+size], fill='#c084fc')

canvas.save('composition.png', quality=95)
```

## Two-Step Process

### Step 1: Design Philosophy (.md)

Write a manifesto for an art movement (4-6 paragraphs) articulating visual essence through:

- **Space**: How elements occupy and interact with the canvas
- **Form**: Shapes, structures, and their relationships
- **Color**: Palette choices and their emotional resonance
- **Material**: Textures and visual weight
- **Scale**: Proportions and visual hierarchy
- **Rhythm**: Repetition, variation, and visual flow
- **Composition**: Arrangement and balance

**Key Emphasis:**
"Meticulously crafted... master-level execution... painstaking attention to detail... countless hours of refinement."

### Step 2: Canvas Expression (.pdf or .png)

Translate philosophy into visual artifacts that are:
- **90% visual design, 10% essential text**
- Minimal, sparse typography
- Sophisticated, museum-quality execution
- Expert-level composition
- No overlapping elements (unless intentional)
- Work appearing as if created by "the absolute top of their field"

## Principles

### Visual Supremacy
Visual information supersedes written explanation. The design should communicate without words.

### Text as Accent
Typography functions as visual accent, not communication vehicle. Use sparingly and purposefully.

### Rewarding Depth
Designs should reward sustained viewing through layered patterns, hidden details, and visual discovery.

### Pristine Quality
Final output must achieve quality suitable for museum display or high-end publication.

### Originality
Create original work only--never copy existing artists or styles directly.

## Implementation

### Using Python (PIL/Pillow)
```python
from PIL import Image, ImageDraw, ImageFont
import math

# Create canvas
width, height = 2400, 3200
canvas = Image.new('RGB', (width, height), '#0a0a0a')
draw = ImageDraw.Draw(canvas)

# Geometric composition
center_x, center_y = width // 2, height // 2

# Primary form - golden ratio spiral
phi = (1 + math.sqrt(5)) / 2
for i in range(50):
    angle = i * phi * 2 * math.pi
    radius = i * 8
    x = center_x + radius * math.cos(angle)
    y = center_y + radius * math.sin(angle)
    size = max(2, 20 - i * 0.3)
    draw.ellipse([x-size, y-size, x+size, y+size], fill='#c084fc')

# Save with high quality
canvas.save('composition.png', quality=95)
```

### Using Cairo (Vector Graphics)
```python
import cairo
import math

width, height = 2400, 3200
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
ctx = cairo.Context(surface)

# Background
ctx.set_source_rgb(0.04, 0.04, 0.04)
ctx.rectangle(0, 0, width, height)
ctx.fill()

# Geometric forms
ctx.set_source_rgba(0.75, 0.52, 0.98, 0.8)
ctx.set_line_width(2)

for i in range(12):
    ctx.save()
    ctx.translate(width/2, height/2)
    ctx.rotate(i * math.pi / 6)
    ctx.move_to(0, 0)
    ctx.line_to(400, 200)
    ctx.stroke()
    ctx.restore()

surface.write_to_png('vector_composition.png')
```

### Using SVG (for PDF conversion)
```python
import svgwrite

dwg = svgwrite.Drawing('composition.svg', size=('24in', '32in'))

# Background
dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='#0a0a0a'))

# Geometric elements
for i in range(20):
    dwg.add(dwg.circle(
        center=(f'{12 + i*0.5}in', f'{16 + i*0.3}in'),
        r=f'{0.5 + i*0.1}in',
        stroke='#c084fc',
        stroke_width=2,
        fill='none'
    ))

dwg.save()

# Convert to PDF with Inkscape or CairoSVG
```

## Visual Styles

### Geometric Minimalism
- Clean lines and shapes
- Monochromatic or limited palette
- Mathematical precision
- Negative space as primary element

### Organic Flow
- Curved, natural forms
- Gradient transitions
- Layered transparency
- Biomorphic shapes

### Structured Chaos
- Grid-based foundation
- Controlled randomness
- Emergent patterns
- Complex from simple rules

### Typographic Art
- Letters as visual elements
- Scale variation
- Spatial composition
- Minimal readable text

## Execution Checklist

- [ ] Philosophy document articulates clear vision
- [ ] Visual work is 90%+ imagery
- [ ] Craftsmanship evident in every detail
- [ ] No sloppy overlaps or misalignments
- [ ] Color palette is intentional and cohesive
- [ ] Composition has clear visual hierarchy
- [ ] Work rewards extended viewing
- [ ] Resolution appropriate for intended use
- [ ] Original--not derivative of specific artists

## Output Specifications

### PNG Format
- Resolution: 300 DPI minimum for print
- Color space: sRGB for web, Adobe RGB for print
- Dimensions: Match intended output size
- Quality: Maximum/lossless compression

### PDF Format
- Vector when possible for scalability
- Embedded fonts if text used
- CMYK for print production
- RGB for screen display

## Error Handling

### Common Issues

**Issue: Artifacts appear pixelated**
- Cause: Low resolution or aggressive compression
- Solution: Use 300+ DPI, quality=95 for PNG

**Issue: Colors print differently than screen**
- Cause: RGB to CMYK conversion
- Solution: Design in CMYK for print, or soft-proof

**Issue: Elements appear misaligned**
- Cause: Floating-point rounding errors
- Solution: Use integer coordinates, snap to grid

**Issue: File size too large**
- Cause: High resolution bitmap
- Solution: Use vector (SVG/PDF) where possible

## Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Resolution | >= 300 DPI | Image properties |
| Visual-to-text ratio | >= 90% visual | Visual inspection |
| Color consistency | Delta E < 3 | Color measurement |
| Alignment precision | < 1px deviation | Grid overlay check |
| File quality | Lossless or quality 95+ | Export settings |

## Philosophy

The goal is creating visual work that appears to have been crafted by someone at the absolute pinnacle of their field--work that demands attention, rewards study, and achieves lasting aesthetic impact.

## Related Skills

- [algorithmic-art](../algorithmic-art/SKILL.md) - Generative art with p5.js
- [frontend-design](../frontend-design/SKILL.md) - Web interface design
- [theme-factory](../theme-factory/SKILL.md) - Color and typography systems

---

## Version History

- **2.0.0** (2026-01-02): Upgraded to v2 template - added Quick Start, When to Use, Execution Checklist, Error Handling, Metrics sections
- **1.0.0** (2024-10-15): Initial release with PIL/Pillow, Cairo, SVG implementations, visual styles, quality guidelines
