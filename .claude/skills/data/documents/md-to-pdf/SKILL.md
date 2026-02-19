# md-to-pdf Skill

Convert Markdown documents with YAML frontmatter into styled, print-ready PDFs using Chrome headless.

## Quick Start

```bash
python3 .claude/skills/data/documents/md-to-pdf/md_to_pdf.py document.md -o output.pdf
```

## When to Use

- Professional reports (GTM strategy, proposals, engineering summaries)
- Any document that needs a styled cover page, section headers, and print-optimized layout
- When you need consistent PDF output without hand-coding HTML

## Prerequisites

- **Chrome**: `/usr/bin/google-chrome` (v145+ recommended)
- **Python**: `markdown` library (v3.5.2+ with tables, fenced_code, toc, attr_list, meta, sane_lists)
- **System Python 3.10+**

## CLI Reference

```
python3 md_to_pdf.py input.md [-o output.pdf] [--screenshot] [--no-cover] [--keep-html] [--template base]
```

| Flag | Description |
|------|-------------|
| `-o`, `--output` | Output PDF path (default: `<input>.pdf`) |
| `--screenshot` | Also generate a QA PNG screenshot |
| `--no-cover` | Skip automatic cover page from frontmatter |
| `--keep-html` | Retain intermediate HTML file for inspection |
| `--template` | Template name from `templates/` (default: `base`) |

## Frontmatter Reference

```yaml
---
title: Document Title
subtitle: Subtitle displayed in accent color
date: February 16, 2026
author: Author Name
version: 1.0
confidentiality: Confidential
accent_color: "#0066cc"
footer: "Company Name | Confidential"
---
```

All fields are optional. `title` defaults to "Untitled Document".

## Component Gallery

### Section Header
```html
<div class="section-header">
  <div class="section-label">SECTION 01</div>
  <h2>Executive Summary</h2>
</div>
```

### Card
```html
<div class="card">
  <h3>Item Name <span class="score-chip score-5">5/5</span></h3>
  <p><span class="field-label">Category:</span> Description text</p>
</div>
```

### Tier Header
```html
<div class="tier-header">Tier 1 — Critical Priority</div>
```

### Score Chips
```html
<span class="score-chip score-5">5/5</span>  <!-- teal -->
<span class="score-chip score-4">4/5</span>  <!-- blue -->
<span class="score-chip score-3">3/5</span>  <!-- orange -->
<span class="score-chip score-2">2/5</span>  <!-- red -->
<span class="score-chip score-1">1/5</span>  <!-- gray -->
```

### Priority Badges
```html
<span class="priority-badge high">High</span>
<span class="priority-badge medium">Medium</span>
<span class="priority-badge low">Low</span>
<span class="priority-badge ongoing">Ongoing</span>
```

### Metric Grid
```html
<div class="summary-grid">
  <div class="metric-card">
    <div class="metric-value">42</div>
    <div class="metric-label">Total Items</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">$1.2M</div>
    <div class="metric-label">Revenue</div>
  </div>
</div>
```

### Standard Markdown (auto-styled)
- **Tables**: dark header, zebra striping — use standard markdown table syntax
- **Blockquotes**: blue left-border callout — use `>` prefix
- **Code blocks**: dark background with monospace — use fenced code blocks
- **Headings**: h1 gets accent underline, h2-h4 styled progressively

### Page Control
```html
<div class="page-break"></div>       <!-- force page break -->
<div class="avoid-break">           <!-- keep content together -->
  ... content ...
</div>
```

## Chrome Flags

The script uses these Chrome headless flags:

| Flag | Purpose |
|------|---------|
| `--headless` | No GUI window |
| `--no-sandbox` | Required in containers/CI |
| `--disable-gpu` | Prevents GPU errors in headless |
| `--print-to-pdf=FILE` | Generate PDF output |
| `--no-pdf-header-footer` | Suppress default Chrome header/footer |
| `--print-background` | Render CSS backgrounds (critical for gradients, chips) |
| `--screenshot=FILE` | Generate PNG for QA |
| `--window-size=W,H` | Viewport for screenshots |

## Integration with Engineering Reports

Existing HTML report generators (wall thickness, dynacard) can reuse `components.css` by including it as a stylesheet. The CSS components are independent of the markdown pipeline.

```python
from pathlib import Path
css = (Path(__file__).parent / "../../.claude/skills/data/documents/md-to-pdf/templates/components.css").read_text()
```

## Browser QA Step

Always use `--screenshot` during development to visually verify layout before final PDF:

```bash
python3 md_to_pdf.py draft.md -o draft.pdf --screenshot --keep-html
# Check draft.png for visual issues
# Check draft.html for template injection correctness
# Final: draft.pdf
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Blank PDF | Chrome not found | Verify `which google-chrome` |
| No background colors | Missing `--print-background` | Already set by default in script |
| Section headers cut off | Missing page-break-before | Use `.section-header` class (has it built-in) |
| Tables split across pages | Large table | Wrap in `<div class="avoid-break">` |
| Accent color wrong | Frontmatter typo | Check `accent_color` is valid CSS color with quotes |
| Cover page missing | `--no-cover` flag | Remove flag, or add frontmatter `title` |
