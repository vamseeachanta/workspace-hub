---
name: theme-factory
description: Professional styling toolkit with 10 pre-set themes for slides, documents, reports, and HTML pages. Use when applying consistent colors and fonts to any artifact, or when generating custom themes on-the-fly.
version: 2.0.0
category: content-design
last_updated: 2026-01-02
related_skills:
  - frontend-design
  - brand-guidelines
  - canvas-design
---

# Theme Factory Skill

## Overview

A curated collection of professional font and color themes with cohesive palettes and complementary typeface pairings suited for diverse contexts. Apply to slides, documents, reports, and HTML pages.

## When to Use

- Applying consistent styling to presentations or documents
- Starting a new project and need a cohesive color scheme
- Creating branded materials without existing guidelines
- Generating HTML reports with professional appearance
- Quick theming for prototypes or demos

## Quick Start

1. **Display themes** - Show all 10 themes with visual swatches
2. **Select theme** - User picks one or requests custom generation
3. **Confirm choice** - Verify before applying
4. **Apply theme** - Inject colors and fonts into artifact

```css
/* Quick apply: Tech Innovation theme */
:root {
  --primary: #0d0221;
  --secondary: #1a0533;
  --accent: #7c3aed;
  --highlight: #a78bfa;
  --text: #f5f3ff;
}
body {
  font-family: 'Space Grotesk', sans-serif;
  background: var(--primary);
  color: var(--text);
}
```

## Available Themes (10 Total)

### 1. Ocean Depths
Deep blues and teals with aquatic undertones.
```css
:root {
  --primary: #0a1628;
  --secondary: #1a365d;
  --accent: #38b2ac;
  --highlight: #4fd1c5;
  --text: #e6fffa;
}
/* Fonts: Outfit (headings), Lora (body) */
```

### 2. Sunset Boulevard
Warm oranges, corals, and golden hues.
```css
:root {
  --primary: #2d1b0e;
  --secondary: #744210;
  --accent: #ed8936;
  --highlight: #fbd38d;
  --text: #fffaf0;
}
/* Fonts: Josefin Sans (headings), Source Serif Pro (body) */
```

### 3. Forest Canopy
Natural greens and earth tones.
```css
:root {
  --primary: #1a2f1a;
  --secondary: #2f4f2f;
  --accent: #48bb78;
  --highlight: #9ae6b4;
  --text: #f0fff4;
}
/* Fonts: Montserrat (headings), Merriweather (body) */
```

### 4. Modern Minimalist
Clean blacks, whites, and grays.
```css
:root {
  --primary: #1a1a1a;
  --secondary: #333333;
  --accent: #666666;
  --highlight: #f5f5f5;
  --text: #ffffff;
}
/* Fonts: Inter (headings), System UI (body) */
```

### 5. Golden Hour
Luxurious golds, bronzes, and creams.
```css
:root {
  --primary: #2c1810;
  --secondary: #5c3d2e;
  --accent: #d69e2e;
  --highlight: #f6e05e;
  --text: #fffff0;
}
/* Fonts: Playfair Display (headings), Crimson Text (body) */
```

### 6. Arctic Frost
Cool whites, silvers, and ice blues.
```css
:root {
  --primary: #0f172a;
  --secondary: #1e293b;
  --accent: #60a5fa;
  --highlight: #e0f2fe;
  --text: #f8fafc;
}
/* Fonts: Poppins (headings), Open Sans (body) */
```

### 7. Desert Rose
Soft pinks, terracotta, and sand.
```css
:root {
  --primary: #3d2c29;
  --secondary: #8b5a4a;
  --accent: #ed8796;
  --highlight: #fce7f3;
  --text: #fdf2f8;
}
/* Fonts: Cormorant Garamond (headings), Nunito (body) */
```

### 8. Tech Innovation
Electric blues, purples, and neons.
```css
:root {
  --primary: #0d0221;
  --secondary: #1a0533;
  --accent: #7c3aed;
  --highlight: #a78bfa;
  --text: #f5f3ff;
}
/* Fonts: Space Grotesk (headings), JetBrains Mono (body) */
```

### 9. Botanical Garden
Rich greens with floral accents.
```css
:root {
  --primary: #14401d;
  --secondary: #1e5631;
  --accent: #76b947;
  --highlight: #a4de8c;
  --text: #ecfccb;
}
/* Fonts: DM Serif Display (headings), Libre Baskerville (body) */
```

### 10. Midnight Galaxy
Deep purples, cosmic blues, and starlight.
```css
:root {
  --primary: #0f0f23;
  --secondary: #1a1a3e;
  --accent: #9333ea;
  --highlight: #c084fc;
  --text: #faf5ff;
}
/* Fonts: Syncopate (headings), Raleway (body) */
```

## Usage Workflow

### Step 1: Display Theme Showcase
Present all 10 themes with visual swatches.

### Step 2: Request User Selection
Ask which theme matches their needs, or offer custom generation.

### Step 3: Confirm Choice
Verify the selection before applying.

### Step 4: Apply Theme
Apply colors and fonts to the artifact.

## Applying Themes

### HTML/CSS
```html
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono&display=swap" rel="stylesheet">

<style>
  :root {
    --primary: #0d0221;
    --secondary: #1a0533;
    --accent: #7c3aed;
    --highlight: #a78bfa;
    --text: #f5f3ff;
  }

  body {
    background: var(--primary);
    color: var(--text);
    font-family: 'JetBrains Mono', monospace;
  }

  h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif;
    color: var(--accent);
  }
</style>
```

### PowerPoint (python-pptx)
```python
from pptx.dml.color import RGBColor

# Tech Innovation theme
THEME = {
    'primary': RGBColor(0x0d, 0x02, 0x21),
    'secondary': RGBColor(0x1a, 0x05, 0x33),
    'accent': RGBColor(0x7c, 0x3a, 0xed),
    'highlight': RGBColor(0xa7, 0x8b, 0xfa),
    'text': RGBColor(0xf5, 0xf3, 0xff),
}

# Apply to shapes
shape.fill.solid()
shape.fill.fore_color.rgb = THEME['primary']
```

### Excel (openpyxl)
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

## Custom Theme Generation

When existing themes don't fit:

### Request Details
1. Purpose (presentation, report, website)
2. Mood (professional, playful, elegant)
3. Brand colors (if any)
4. Industry context

### Generate Custom
```css
/* Custom theme based on user input */
:root {
  --primary: /* derived from context */;
  --secondary: /* complementary shade */;
  --accent: /* attention-grabbing contrast */;
  --highlight: /* lighter accent variant */;
  --text: /* readable on primary */;
}
```

### Font Selection
- **Headings**: Match tone (modern, classic, technical)
- **Body**: Ensure readability and complement headings
- **Fallbacks**: Always include system fonts

## Quick Reference

| Theme | Mood | Best For |
|-------|------|----------|
| Ocean Depths | Professional, calm | Corporate, healthcare |
| Sunset Boulevard | Warm, inviting | Hospitality, food |
| Forest Canopy | Natural, sustainable | Environment, wellness |
| Modern Minimalist | Clean, neutral | Any industry |
| Golden Hour | Luxurious, premium | Finance, luxury brands |
| Arctic Frost | Cool, tech-forward | SaaS, analytics |
| Desert Rose | Soft, approachable | Beauty, lifestyle |
| Tech Innovation | Cutting-edge, bold | Startups, tech |
| Botanical Garden | Fresh, organic | Food, wellness |
| Midnight Galaxy | Creative, mysterious | Entertainment, gaming |

## Execution Checklist

- [ ] Presented theme options to user
- [ ] Confirmed theme selection
- [ ] Loaded appropriate Google Fonts
- [ ] Applied CSS variables to document
- [ ] Verified contrast ratios meet accessibility
- [ ] Tested in both light and dark contexts
- [ ] Documented theme choice for future reference

## Error Handling

### Common Issues

**Issue: Fonts not loading**
- Cause: Missing Google Fonts import or network issue
- Solution: Verify import URL, add fallback fonts in font-family

**Issue: Colors look washed out**
- Cause: Theme designed for dark mode used on light background
- Solution: Swap primary/text colors or choose light-mode theme

**Issue: Poor contrast ratio**
- Cause: Using accent color for body text
- Solution: Use text color for body, accent only for highlights

**Issue: Theme doesn't match brand**
- Cause: Using preset without customization
- Solution: Generate custom theme with brand colors as inputs

## Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Color Contrast (text) | >= 4.5:1 | WebAIM Contrast Checker |
| Color Contrast (large text) | >= 3:1 | WebAIM Contrast Checker |
| Font Load Time | < 500ms | Network DevTools |
| Theme Consistency | 100% | Manual audit |

## Related Skills

- [frontend-design](../frontend-design/SKILL.md) - Custom UI development
- [brand-guidelines](../../communication/brand-guidelines/SKILL.md) - Full brand systems
- [canvas-design](../canvas-design/SKILL.md) - Visual art creation

---

## Version History

- **2.0.0** (2026-01-02): Upgraded to v2 template - added Quick Start, When to Use, Execution Checklist, Error Handling, Metrics sections
- **1.0.0** (2024-10-15): Initial release with 10 curated themes, HTML/CSS, PowerPoint, Excel integration, custom generation
