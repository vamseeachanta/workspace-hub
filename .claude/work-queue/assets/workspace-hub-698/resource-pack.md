# Resource Pack: WRK-663

## Problem Context
The pending work queue has grown to 160+ items, many of which are stale, misclassified, or duplicates. Managing such a large backlog manually is inefficient. WRK-663 uses Gemini's large context window to triage the entire queue in one pass, identifying quick wins and cleaning up dead weight.

## Relevant Documents/Data
- `.claude/work-queue/pending/`: The source directory for analysis.
- `specs/wrk/WRK-663/pending-queue-snapshot.txt`: The data captured for Gemini analysis.
- `scripts/work-queue/INDEX.md`: The summary index used for priority distribution analysis.

## Constraints
- Triage must be consistent across items (same criteria for QUICK-WIN, etc.).
- Analysis must result in actionable moves (cancel, unblock, re-prioritize).
- Changes must not break `generate-index.py` validation.

## Assumptions
- Frontmatter in WRK items is mostly accurate regarding `complexity` and `blocked_by`.
- Gemini 1.5 Pro can handle the ~10k lines of snapshot text in 1-2 chunks.

## Open Questions
- Should "personal errands" be deleted or just moved to `done/`? (Decision: move to `done/` with a cancellation note for traceability).

## Domain Notes
- This is a meta-queue management task.
