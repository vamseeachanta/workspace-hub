# WRK-1115 Plan: Unified Plan+Lifecycle HTML

## Context

Currently `generate-html-review.py` emits only one HTML file per WRK
(`WRK-NNN-lifecycle.html`). Several stages (12, 13) have no dedicated renderers,
Stage 10 drops rich execution data, Stage 14 drops gate detail strings, and there
is no stable "plan document" URL. This work introduces a second canonical file
(`plan.html`) and fills the rendering gaps, so users can review work quality at
a glance by refreshing two stable URLs.

---

## Files to Change

| File | Change |
|------|--------|
| `scripts/work-queue/generate-html-review.py` | Add `--plan` flag + `generate_plan()`, expand stage renderers |
| `scripts/work-queue/exit_stage.py` | Call both `--lifecycle` and `--plan` after every stage exit |
| `.claude/skills/workspace-hub/workflow-html/SKILL.md` | Update to two-file contract |
| `tests/unit/test_generate_html_review.py` | ≥8 new tests |

---

## Phase 1 — Expand Existing Lifecycle Renderers

All changes are in `render_lifecycle_stage_body()`.

### Stage 10 (lines 1695–1706)
Add after existing 4-field schema block:
- **`integrated_repo_tests`**: render as `<table>` with columns Name / Result / Command (truncated to 60 chars). PASS → green badge, FAIL → red badge.
- **`changes[]`**: render as `<ul>` bullet list under label "What changed".

### Stage 12 — new renderer (before default fallback at line 1808)
Read `assets/WRK-NNN/ac-test-matrix.md`. Parse markdown table rows. Render:
- Summary badge: "N PASS · M FAIL"
- Full table with Result cell coloured (PASS=green, FAIL=red, N/A=muted).
- Graceful: if file absent → "ac-test-matrix.md not yet written."

### Stage 13 — new renderer
Reuse Stage 6 cross-review renderer logic. Glob `evidence/cross-review-impl*.md`
and `evidence/cross-review-impl*.yaml`. Render verdict badges + findings summary.
Graceful: if absent → "Cross-review not yet complete."

### Stage 14 (lines 1729–1750)
Add third column `Details` to the gate table. Truncate details string to 120 chars.

### Stage duration headers (all stages)
Read `evidence/stage-evidence.yaml`. For each stage section header, if the stage
entry has a non-empty `comment`, append it as a small muted subtitle. If a
`completed_at` timestamp exists on the stage entry, show elapsed time.
(Graceful: skip if `stage-evidence.yaml` absent or stage entry has no timestamp.)

---

## Phase 2 — New `generate_plan()` + `--plan` Flag

### New function: `generate_plan(wrk_id, output_file=None)`

Output path: `assets/WRK-NNN/WRK-NNN-plan.html`

**Sections (top to bottom):**

1. **HERO** — same design system as lifecycle; title = WRK title + "(Plan)";
   `<meta http-equiv="refresh" content="30">`.

2. **Stage-circle progress strip** — reuse `detect_stage_statuses()` +
   existing strip-chip render code verbatim.

3. **Latest plan** — extract `## Plan` section from WRK `.md` body via regex.
   Render as markdown → HTML using existing `markdown.markdown()` call.
   Label: "Current Plan (as of Stage N)".

4. **Per-stage change log** — read `evidence/plan-changelog.yaml` (new optional
   file; schema: list of `{stage, summary, changed_at}`). Render as collapsible
   sections per stage entry. If absent: show "No plan changes recorded."

### `--plan` flag

Add to argparse block (line ~2102):
```python
parser.add_argument("--plan", action="store_true",
                    help="Generate plan HTML (WRK-NNN-plan.html)")
```

Main dispatch: `if args.plan: generate_plan(args.wrk_id, args.output)`

Both `--plan` and `--lifecycle` (or no flag) work independently.

---

## Phase 3 — `exit_stage.py` Hook

Rename `_regenerate_lifecycle_html()` → keep name but add a second subprocess call:

```python
subprocess.run([...script..., wrk_id, "--plan"], ...)
```

Both calls run unconditionally after every successful stage exit. Failure of
`--plan` call logs a warning but does not fail the stage exit (non-blocking).

---

## Phase 4 — `workflow-html/SKILL.md` Update

- Change heading "Single Lifecycle HTML Model" → "Two-File HTML Model"
- Document `plan.html`: path, sections, when created (after stage 4b), auto-refresh
- Update file lifecycle table to show both files
- Add `plan-changelog.yaml` schema reference

---

## TDD — Tests to Write

All in `tests/unit/test_generate_html_review.py`, using existing `tmp_path` +
`monkeypatch(os.popen)` pattern:

| # | Test name | Assertion |
|---|-----------|-----------|
| 1 | `test_plan_html_generated` | `--plan` flag creates `WRK-NNN-plan.html` |
| 2 | `test_plan_html_has_meta_refresh` | plan.html contains `meta http-equiv="refresh" content="30"` |
| 3 | `test_plan_html_has_stage_circles` | plan.html contains stage-strip markup |
| 4 | `test_plan_html_shows_plan_text` | plan.html includes text from `## Plan` section |
| 5 | `test_stage10_renders_integrated_tests` | Stage 10 section contains test name + PASS badge |
| 6 | `test_stage12_renders_ac_test_matrix` | Stage 12 section contains PASS/FAIL table from ac-test-matrix.md |
| 7 | `test_stage13_renders_cross_review` | Stage 13 section contains verdict from cross-review-impl.yaml |
| 8 | `test_stage14_shows_details_column` | Stage 14 gate table contains details text |

---

## Verification

```bash
# Run tests
uv run --no-project python -m pytest tests/unit/test_generate_html_review.py -v

# Manual smoke test against a real WRK
uv run --no-project python scripts/work-queue/generate-html-review.py WRK-1114 --lifecycle
uv run --no-project python scripts/work-queue/generate-html-review.py WRK-1114 --plan

# Confirm both files exist
ls .claude/work-queue/assets/WRK-1114/WRK-1114-{lifecycle,plan}.html

# Confirm exit_stage calls both
uv run --no-project python scripts/work-queue/exit_stage.py WRK-1115 3  # dry run on a safe stage
```
