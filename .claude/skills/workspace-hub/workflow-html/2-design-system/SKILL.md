---
name: workflow-html-2-design-system
description: 'Sub-skill of workflow-html: 2. Design System.'
version: 2.3.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# 2. Design System

## 2. Design System


Warm-parchment design system — all WRK HTML artifacts share it; never deviate. Key tokens:
`--bg:#f3efe6`, `--panel:#fffdf8`, `--ink:#172126`, `--accent:#0f766e` (teal),
`--accent-2:#8a5a2b` (amber), `--good:#166534`, `--warn:#b45309`, `--bad:#b91c1c`.

Body: Georgia serif, radial-gradient background. Code: SFMono monospace.
Layout: `.hero`, `.card`, `.exec-summary`, `.split` (2-col CSS grid, 1-col ≤900px).
Stage chips: `sc-done` (teal) | `sc-active` (amber) | `sc-pending` (grey) | `sc-na`.
Status badges: `b-done` | `b-active` | `b-pending` | `b-na`.

Full CSS inline in `generate-html-review.py` — do not duplicate or hand-edit HTML output.

---
