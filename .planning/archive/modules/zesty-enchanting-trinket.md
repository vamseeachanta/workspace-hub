# WRK-1159: Auto-open lifecycle HTML in browser at human-gate stages

## Context

`start_stage.py` generates lifecycle HTML at every stage entry but never opens it in a browser. The existing `log-user-review-browser-open.sh` handles cross-platform browser opening + evidence logging, but is never called automatically. Users arriving at human-gate stages (5, 7, 17) have no visibility into the HTML review artifacts.

## Plan

### 1. Modify `scripts/work-queue/start_stage.py`

**Change A — Extend `_regenerate_lifecycle_html()` (line 327):**
- Add `--plan` generation alongside existing `--lifecycle` call
- Loop over both modes so both HTML files exist before any browser open

**Change B — Add `_auto_open_html_for_human_gates()` (after line 341):**
- Stage map constant: `{5: "plan_draft", 7: "plan_final", 17: "close_review"}`
- Double-open prevention: read `user-review-browser-open.yaml`, skip if stage already has an event
- For each HTML file (lifecycle + plan): call `log-user-review-browser-open.sh` via subprocess
- Gracefully skip missing HTML files with a warning

**Change C — Wire the call (line 485):**
- Add `_auto_open_html_for_human_gates(wrk_id, stage, repo_root)` after `_regenerate_lifecycle_html()`

### 2. Create `scripts/work-queue/tests/test_auto_open_html.py` (TDD first)

| # | Test | Covers |
|---|------|--------|
| 1 | `test_skips_non_human_gate_stages` | Stages 2, 3, 8, 12 → no subprocess calls |
| 2 | `test_opens_both_html_for_stage_5` | Stage 5 → calls browser script twice with `plan_draft` |
| 3 | `test_stage_7_maps_to_plan_final` | Stage 7 → `plan_final` |
| 4 | `test_stage_17_maps_to_close_review` | Stage 17 → `close_review` |
| 5 | `test_skips_when_already_opened` | Pre-populated evidence → no subprocess calls |
| 6 | `test_skips_missing_html_gracefully` | Missing HTML files → warning, no crash |

### 3. No other files modified

`log-user-review-browser-open.sh` and `generate-html-review.py` used as-is.

## Critical files

- `scripts/work-queue/start_stage.py` — core modification (3 changes)
- `scripts/work-queue/log-user-review-browser-open.sh` — called as subprocess (no changes)
- `scripts/work-queue/generate-html-review.py` — called with `--plan` flag (no changes)

## Verification

1. Run tests: `uv run --no-project python -m pytest scripts/work-queue/tests/test_auto_open_html.py -v`
2. Manual: `uv run --no-project python scripts/work-queue/start_stage.py WRK-1148 5` — confirm both HTML files open in browser
3. Confirm evidence in `assets/WRK-1148/evidence/user-review-browser-open.yaml`
4. Re-run same command — confirm no duplicate browser opens
