---
title: md-to-pdf skill — Markdown to styled PDF via Chrome headless
description: Build a reusable md-to-pdf skill with HTML template, print CSS components, and Chrome headless PDF generation
version: 1.0.0
module: md-to-pdf
session:
  id: 2026-02-16-gtm-analysis
  agent: claude-opus-4-6
review: pending
---

# md-to-pdf Skill

## Context

Every time a professional PDF is needed (GTM strategy, proposals, engineering reports), the workflow is reinvented from scratch — hand-coded HTML, fighting wkhtmltopdf, debugging page breaks. The styled GTM strategy PDF (v3) proved that **Chrome browser print** produces good results when the HTML/CSS is right. This skill systematizes that workflow.

**What exists**: 4 PDF skills for reading/extraction, zero for generation. Chrome 145 available at `/usr/bin/google-chrome`. Python `markdown` library v3.5.2 already installed with tables/fenced_code/attr_list extensions. Existing HTML report generators (wall thickness, dynacard) use Plotly but have no `@media print` optimization.

## Deliverables (5 files)

### 1. `md_to_pdf.py` — Main script (~200 lines)

**Path**: `.claude/skills/data/documents/md-to-pdf/md_to_pdf.py`

**Flow**: Read .md → parse YAML frontmatter → convert body via `markdown` lib → build cover page from metadata → inject into base.html template → write temp HTML → Chrome `--screenshot` (QA) → Chrome `--print-to-pdf` → output PDF

**CLI**:
```
python3 md_to_pdf.py input.md [-o output.pdf] [--screenshot] [--no-cover] [--keep-html] [--template base]
```

**Key functions**:
- `parse_frontmatter(text)` → `(metadata_dict, body)` — regex-based `---` block parser
- `convert_md_to_html(body)` → `html` — uses `markdown.Markdown(extensions=[tables, fenced_code, toc, attr_list, meta, sane_lists])`
- `build_cover_page(meta)` → `<div class="cover-page">` with accent bar, title, subtitle, date, confidentiality
- `inject_into_template(cover, body, meta)` → full HTML string with CSS inlined
- `screenshot(html_path, png_path)` → Chrome `--screenshot`
- `generate_pdf(html_path, pdf_path)` → Chrome `--print-to-pdf`

**Chrome commands**:
```bash
# PDF
google-chrome --headless --no-sandbox --disable-gpu \
  --print-to-pdf=output.pdf --no-pdf-header-footer --print-background \
  file:///path/to/input.html

# Screenshot (QA)
google-chrome --headless --no-sandbox --disable-gpu \
  --screenshot=output.png --window-size=1200,1600 \
  file:///path/to/input.html
```

### 2. `templates/base.html` — HTML shell (~30 lines)

**Path**: `.claude/skills/data/documents/md-to-pdf/templates/base.html`

Minimal shell with `{{CSS}}`, `{{COVER}}`, `{{BODY}}`, `{{TITLE}}`, `{{FOOTER_TEXT}}` placeholders. No template engine — plain string `.replace()`.

### 3. `templates/components.css` — Reusable styles (~300 lines)

**Path**: `.claude/skills/data/documents/md-to-pdf/templates/components.css`

10 component classes derived from the GTM styled PDF:

| Component | CSS Class | Use |
|-----------|-----------|-----|
| Cover page | `.cover-page` | Title page with accent bar, page-break-after |
| Section header | `.section-header` | Dark navy gradient, "SECTION 01" label |
| Card | `.card` | White bordered card for entity entries |
| Tier header | `.tier-header` | Gray background strip for grouping |
| Score chip | `.score-chip.score-5` through `.score-1` | Color-coded round badges (teal/blue/orange/red/gray) |
| Priority badge | `.priority-badge.high/.medium/.low/.ongoing` | Color-coded rectangular badges |
| Quote box | `blockquote` | Blue left-border callout |
| Metric grid | `.summary-grid` + `.metric-card` | CSS Grid of stat cards |
| Tables | `table` | Styled headers, zebra striping |
| Page control | `.page-break`, `.avoid-break` | Print layout control |

Plus `@page { size: A4; margin: 20mm 15mm 25mm 15mm; }` and `@media print` rules (hide Plotly toolbar, enforce backgrounds).

### 4. `SKILL.md` — Skill definition (~180 lines)

**Path**: `.claude/skills/data/documents/md-to-pdf/SKILL.md`

Sections: Overview, Quick Start, When to Use, Prerequisites, Frontmatter Reference, Component Gallery (markdown examples for each CSS class), Chrome Flags, Integration with Engineering Reports, Browser QA Step, Troubleshooting.

### 5. Command file (~25 lines)

**Path**: `.claude/commands/data/md-to-pdf.md`

Standard frontmatter + usage + examples + `@.claude/skills/data/documents/md-to-pdf/SKILL.md` reference.

## Markdown Authoring Convention

Frontmatter controls the cover page:
```yaml
---
title: Document Title
subtitle: Subtitle in blue
date: February 16, 2026
confidentiality: Confidential
accent_color: "#0066cc"
footer: "Company Name"
---
```

Custom components use raw HTML blocks (markdown lib passes through HTML unchanged):
```html
<div class="section-header">
  <div class="section-label">SECTION 01</div>
  <h2>Section Title</h2>
</div>

<div class="card">
  <h3>Item <span class="score-chip score-5">5/5</span></h3>
  <p><span class="field-label">Why:</span> Reason text</p>
</div>
```

Standard markdown (headings, tables, blockquotes, lists, code blocks) styles automatically.

## Design Decisions

1. **Use `markdown` library** (already installed v3.5.2) — not regex-based
2. **Single base template** with modular CSS — not multiple template files
3. **Chrome headless** (not wkhtmltopdf) — confirmed working, respects CSS properly
4. **String `.replace()`** for template injection — avoids Jinja2 dependency
5. **`@page` CSS** controls margins/size — not Chrome `--no-margins` flag
6. **`--print-background`** flag — critical for section header gradients and colored chips

## Verification

1. Create a test markdown with all 10 components
2. Run: `python3 .claude/skills/data/documents/md-to-pdf/md_to_pdf.py test.md -o test.pdf --screenshot --keep-html`
3. Check `test.png` screenshot visually
4. Check `test.pdf` opens and renders correctly
5. Verify cover page, section headers, cards, tables, score chips all display
6. Verify page breaks work (section headers start on new pages)
7. Check `test.html` intermediate file for correct template injection
