---
name: workflow-html-1-good-practices
description: 'Sub-skill of workflow-html: 1. Good Practices.'
version: 2.3.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# 1. Good Practices

## 1. Good Practices


Rules MUST be followed for HTML consistency across all WRK items:

1. **Shared CSS only** — both HTML files use identical `SHARED_CSS` from the generator;
   never introduce file-specific CSS variables or override inline styles for tables/chips.
2. **Sticky stage strip** — both files have the same sticky `.stage-strip` nav with
   numbered circles reflecting actual stage status from `evidence/stage-evidence.yaml`.
3. **Hero chips are identical across both files** —
   Row 1: `Now (amber) · Status (amber) · Workstation · Orchestrator · Created`;
   Row 2: `Repo · Category · Subcategory · Priority · Route`.
   Use `.meta-break` (flex-basis:100%) to force the row split. `pill-stage` = amber.
   Eyebrow: `WRK-NNN · LIFECYCLE TRACKER` / `WRK-NNN · PLAN DOCUMENT` — no route/stage.
4. **Markdown rendering** — `plan.html` runs `renderMarkdown()` JS on `.plan-body` at
   `DOMContentLoaded`; supports headings, pipe tables, bold/italic, code blocks.
5. **Auto-refresh** — both files have `<meta http-equiv="refresh" content="30">`.
6. **Branding footer** — both files end with `<footer class="brand-footer">` containing
   the digitalmodel logo mark.
7. **No external deps** — all CSS and JS is inline; no CDN, no external fonts; uses system
   `Georgia` serif / `SFMono` monospace stack.
8. **Windows compatibility** — `file://` URLs work via `start` or file explorer;
   `python -m http.server` preferred; no Linux-specific paths hardcoded in HTML output.
9. **Table-first data display** — render multi-field evidence sets, comparisons, and lists
   as `<table>` (not prose or `.schema-row` grids where tabular data fits better).
   Always use the `_render_table(headers, rows_html, compact=False)` helper — it produces
   correct `<thead>`/`<tbody>` structure; never emit bare `<table><tr><th>` or inline
   `style=` on table elements. Use `compact=True` for dense inline contexts.

---
