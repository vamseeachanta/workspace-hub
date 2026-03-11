---
name: workflow-html
description: >
  Canonical HTML system for WRK items. Two files per WRK: WRK-NNN-lifecycle.html (20-stage
  progress) and WRK-NNN-plan.html (plan text + stage-circle strip + change log). Both generated
  by generate-html-review.py (--lifecycle / --plan) and regenerated on every stage exit via
  exit_stage.py. Defines the warm-parchment design system, rendering rules, and evidence-driven
  stateless generation. No manual HTML editing required.
version: 2.3.0
updated: 2026-03-11
category: workspace-hub
type: skill
trigger: manual
auto_execute: false
capabilities: [lifecycle_html_generation, stage_status_detection, evidence_driven_rendering, design_system]
related_skills: [workspace-hub/workflow-gatepass, workspace-hub/work-queue-workflow, workspace-hub/wrk-lifecycle-testpack]
tools: [Read, Write, Bash]
see_also: [scripts/work-queue/generate-html-review.py]
---

# Workflow HTML Skill

> Canonical HTML template and design system for all WRK review artifacts.

---

## 0. Two-File HTML Model

**Two HTML files per WRK**, both in `.claude/work-queue/assets/WRK-NNN/`:

| File | Purpose | Created at |
|------|---------|-----------|
| `WRK-NNN-lifecycle.html` | 20-stage progress, evidence, gate results | Stage 1 |
| `WRK-NNN-plan.html` | Latest plan text, stage-circle strip, change log | Stage 4b |

`plan-changelog.yaml` schema: list of `{stage, summary, changed_at}`.
Absent file → "No plan changes recorded." graceful fallback.

### Commands

```bash
# Regenerate both files
uv run --no-project python scripts/work-queue/generate-html-review.py WRK-NNN --lifecycle
uv run --no-project python scripts/work-queue/generate-html-review.py WRK-NNN --plan

# Serve locally (cross-platform)
cd .claude/work-queue/assets/WRK-NNN && python -m http.server 7782
# Then open: http://localhost:7782/WRK-NNN-lifecycle.html

# Both files auto-regenerate on every stage exit (exit_stage.py --lifecycle + --plan)
```

---

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

## 3. Lifecycle Structure

### 3.1 Stage Section Schema

Each stage is `<section class="stage-section" id="sN">` with `.stage-header onclick=toggle()`,
`.stage-title` (num + name + badge), and `.stage-body`. Gate stages (5, 7, 17) get a `b-gate`
badge. Done/active stages start expanded; pending/na start collapsed (`stage-body collapsed`).

Stage 7 gate-checker fields must appear at line-start (no HTML wrapping) so
`check_plan_confirmation()` can parse `confirmed_by:`, `confirmed_at:`, `decision:`.

### 3.2 Stage Evidence Sources

| Stages | Evidence file(s) |
|--------|-----------------|
| 1 | WRK frontmatter |
| 2 | `evidence/resource-intelligence.yaml` |
| 3 | frontmatter `complexity` + `route` |
| 4 | `## Plan` in WRK body |
| 5 | `evidence/user-review-plan-draft.yaml` |
| 6 | `evidence/cross-review*.md` |
| 7 | `evidence/user-review-plan-final.yaml` |
| 8–9 | `evidence/claim.yaml` |
| 10 | `evidence/execute.yaml` |
| 11, 14 | `evidence/gate-evidence-summary.json` |
| 12 | `evidence/test-results.yaml` |
| 13 | `evidence/cross-review-impl.md` |
| 15 | `evidence/future-work.yaml` |
| 16 | `evidence/resource-intelligence-update.yaml` |
| 17 | `evidence/user-review-close.yaml` |
| 18 | `evidence/reclaim.yaml` (or `na`) |
| 19 | frontmatter `status: done` |
| 20 | WRK file in `archive/` |

---

## 4. Gate Artifact Format Reference

| Gate | Expected file | Key fields |
|------|--------------|-----------|
| Plan confirmation | `WRK-NNN-lifecycle.html` Stage 7 | `confirmed_by:`, `confirmed_at:`, `decision: passed` |
| Browser-open | `evidence/user-review-browser-open.yaml` | `stage: plan_draft\|plan_final\|close_review` |
| Cross-review | `review.md` or `review.html` | verdict field |
| Stage evidence | `evidence/stage-evidence.yaml` | all 20 stages with status |
| Resource intel | `evidence/resource-intelligence.yaml` | `completion_status`, `skills.core_used` ≥3 |
| Future work | `evidence/future-work.yaml` | `recommendations[]` with `captured: true` |

---

## 5. Generator Script Integration

`scripts/work-queue/generate-html-review.py` — `--type` flags deprecated (WRK-1031). Use `--lifecycle`.

```python
def generate_lifecycle(wrk_id: str, output_file: str | None = None) -> None:
    """Generate WRK-NNN-lifecycle.html from evidence files on disk (stateless)."""
```

`detect_stage_statuses()` reads evidence files → `{stage_n: 'done'|'active'|'pending'|'na'}`.
Re-running `--lifecycle` is idempotent — safe at any stage gate.

---

## 6. Mandatory Usage

| Stage | Trigger | Action |
|-------|---------|--------|
| 5 | After `user-review-plan-draft.yaml` | `generate-html-review.py WRK-NNN --lifecycle` |
| 7 | After `user-review-plan-final.yaml` | `generate-html-review.py WRK-NNN --lifecycle` |
| 11 | After execution phase | `generate-html-review.py WRK-NNN --lifecycle` |
| 17 | Before user close review | `generate-html-review.py WRK-NNN --lifecycle` |
| 19 | Auto-called by `close-item.sh` | `generate-html-review.py WRK-NNN --lifecycle` |

```bash
xdg-open .claude/work-queue/assets/WRK-NNN/WRK-NNN-lifecycle.html
# log: via scripts/work-queue/log-user-review-browser-open.sh
```

---

## 7. Compliance Checklist

```
[ ] Generated via generate-html-review.py WRK-NNN --lifecycle (uv run --no-project)
[ ] Design system: warm-parchment CSS variables present (--bg #f3efe6, --accent #0f766e)
[ ] Hero: eyebrow=WRK-ID, H1=title, all meta pills populated
[ ] Stage strip: 20 chips; done=teal, active=amber, pending=grey
[ ] 20 stage sections present (id="s1" through id="s20")
[ ] Active stage expanded; pending/na collapsed
[ ] Gate stages (5, 7, 17) have "gate" badge; stage toggle JS present
[ ] File opened in browser and signal logged
```

---

## Version History

- **2.3.0** (2026-03-11): Unified hero chips across both files (same 2-row layout); Status amber (pill-stage); Category+Subcategory row 2; `.meta-break` CSS; stage banner `Stage N: Name ── START/DONE/WAITING` in checkpoint_writer + start_stage
- **2.2.0** (2026-03-11): Rule 9 (table-first); unified table CSS; _render_table() object model; lifecycle hero chips (Status/Priority/Workstation/Orchestrator/Created); dynamic lede
- **2.1.0** (2026-03-11): Good Practices section; Commands reference; condensed to ≤200 lines
- **2.0.0** (2026-03-10): Two-file model (lifecycle + plan); plan-changelog.yaml schema
- **1.5.0** (2026-03-07): Stateless generator; `--lifecycle`; `detect_stage_statuses()`; 63 tests (WRK-1031)
- **1.4.0** (2026-03-07): Single lifecycle HTML; stage section schema; approval-block (WRK-1026)
- **1.3.0** (2026-03-05): `.panel` primitive; evidence-driven plan source (WRK-1011)
- **1.1.0** (2026-03-04): `_suppress_duplicate_generated_sections()`; 29 unit tests
