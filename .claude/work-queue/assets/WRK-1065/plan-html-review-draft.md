# WRK-1065 Plan Draft

## Summary
Context budget monitor: auto-checkpoint at 80% + session chunking guide.

## Steps
1. `scripts/hooks/context-monitor.sh` — log at 70%/80%; checkpoint at 80%
2. `.claude/docs/session-chunking.md` — chunking guidance doc
3. Edit Stage 10 in `work-queue-workflow/SKILL.md` — add context budget note
4. `tests/hooks/test-context-monitor.sh` — TDD shell tests

## Test Strategy
- Unit: test-context-monitor.sh validates log format and checkpoint invocation
- Manual: run script with mock usage pct values, verify output

## Route
A (simple) — single-session execution.

## Confirmation
confirmed_by: vamsee
confirmed_at: 2026-03-09T11:25:00Z
decision: passed
