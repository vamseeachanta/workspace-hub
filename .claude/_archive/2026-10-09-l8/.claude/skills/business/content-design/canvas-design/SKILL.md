---
name: canvas-design
description: Create original visual art, static infographics, and data-backed visual artifacts in PNG and PDF formats using design philosophy principles. Use for museum-quality visual artifacts, design manifestos, artistic compositions, and stakeholder-facing risk/safety infographics.
type: reference
version: 2.0.0
category: business
last_updated: 2026-01-02
related_skills:
- algorithmic-art
- frontend-design
- theme-factory
capabilities: []
requires: []
tags: []
---

# Canvas Design

## Overview

This skill guides creation of original visual art, static infographics, and data-backed visual artifacts in PNG and PDF formats using design philosophy principles. Emphasize craftsmanship and visual hierarchy; use minimal text for art pieces, but allow concise evidence labels and provenance for stakeholder-facing infographics.

## When to Use

- Creating museum-quality visual artifacts
- Generating design manifestos with visual expression
- Building artistic compositions for presentations or publications
- Producing abstract art for branding or decoration
- Creating data-backed risk infographics from a source document plus repository datasets
- Any project requiring 90%+ visual design with minimal text

## Data-Backed Risk Infographics

When the artifact is meant to show avoidable risk using operational or incident data, use the workflow in [references/data-backed-risk-infographics.md](references/data-backed-risk-infographics.md): extract document themes, compute a statistics sidecar, produce HTML plus PNG/PDF exports, and verify rendered readability/clipping before handoff.

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

## Related Skills

- [algorithmic-art](../algorithmic-art/SKILL.md) - Generative art with p5.js
- [frontend-design](../frontend-design/SKILL.md) - Web interface design
- [theme-factory](../theme-factory/SKILL.md) - Color and typography systems

---

## Version History

- **2.0.0** (2026-01-02): Upgraded to v2 template - added Quick Start, When to Use, Execution Checklist, Error Handling, Metrics sections
- **1.0.0** (2024-10-15): Initial release with PIL/Pillow, Cairo, SVG implementations, visual styles, quality guidelines

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
- [Metrics](metrics/SKILL.md)

## Sub-Skills

- [Step 1: Design Philosophy (.md) (+1)](step-1-design-philosophy-md/SKILL.md)
- [Visual Supremacy (+4)](visual-supremacy/SKILL.md)
- [Using Python (PIL/Pillow) (+2)](using-python-pilpillow/SKILL.md)
- [Geometric Minimalism (+3)](geometric-minimalism/SKILL.md)
- [PNG Format (+1)](png-format/SKILL.md)
- [Philosophy](philosophy/SKILL.md)
