# Plan: WRK-663 — Queue Triage

## Goal
Classify the 160+ pending work items into actionable categories and identify the top 10 immediate implementation candidates.

## Proposed Changes

### Phase 1 — Snapshot & Analysis
- Capture the frontmatter of all files in `.claude/work-queue/pending/`.
- Use Gemini to classify items as QUICK-WIN, STALE-BLOCKER, MISCLASSIFIED, DUPLICATE, CANCEL, or SKIP-MACHINE.

### Phase 2 — Execution of Recommendations
- **CANCEL**: Move out-of-scope/personal items to `done/` with a note.
- **UNBLOCK**: Remove completed dependencies from `blocked_by` and move to `pending/`.
- **RE-PRIORITIZE**: Flag QUICK-WINS as `priority: high`.

### Phase 3 — Reporting
- Generate `specs/wrk/WRK-663/queue-triage-report.md`.
- Regenerate `INDEX.md`.

## Verification Plan

### Automated Tests
- `python3 .claude/work-queue/scripts/generate-index.py` (Validation of queue state).

### Smoke Tests
- Verify that "CANCEL" items no longer appear in the pending list.
- Verify that the TOP-10 list correctly reflects the unblocked state of the items.

## Acceptance Criteria
- [x] Full triage report generated.
- [x] Out-of-scope items (e.g., Heriberto) cancelled.
- [x] Index regenerated and valid.
