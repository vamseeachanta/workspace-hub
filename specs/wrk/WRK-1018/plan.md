# WRK-1018 Plan — scan-future-work Phase 6 integration

## Route
Route A (simple)

## Plan
1. Create `scripts/work-queue/scan-future-work.py` — scan `assets/*/evidence/future-work.yaml` for `captured: false` items within 30-day window; output to candidates file for Phase 7.
2. Update `pipeline-detail.md` Phase 6 — add future-work surfacing step after WRK feedback loop analysis; include skip guard if script absent.
3. Legal scan before commit; manual smoke-test verification.

## Approved by
vamsee (2026-03-10T23:35:00Z) — inline approval "I approve stage 1"
