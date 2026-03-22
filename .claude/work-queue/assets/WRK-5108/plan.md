# WRK-5108 Plan

## Phase 1 — Audit usage patterns
- Scan session logs across claude, codex, gemini providers
- Map which scripts in `scripts/work-queue/` are actually invoked

## Phase 2 — Identify dead code
- Cross-reference audit results against all scripts
- Flag scripts with zero invocations or redundant overlaps

## Phase 3 — Prune & consolidate
- Archive one-time migration scripts
- Remove confirmed dead code

## Phase 4 — Verify
- Smoke test all retained scripts
- End-to-end `/work` workflow validation

## Confirmation
confirmed_by: vamseeachanta
confirmed_at: 2026-03-21T23:08:19Z
decision: passed
