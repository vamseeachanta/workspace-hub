# WRK-690 Lessons Applied

Date: 2026-03-04

## Key Lessons That Unblocked Progress

1. Separate **measured** from **inferred** signal coverage in reporting.
   Inferred signals are advisory and must never be treated as measured compliance.
2. Emit gate signals from shared workflow scripts so all orchestrators/providers
   contribute with the same contract.
3. Standardize gate logs to include explicit `signal:` for machine parsing.
4. Rebuild weekly analysis from native stores before audit; do not audit stale
   snapshots.
5. Keep per-agent source coverage visible to catch provider-specific drift hidden
   by aggregate totals.

## Where Lessons Were Applied

- `.claude/skills/workspace-hub/comprehensive-learning/SKILL.md`
- `.claude/skills/workspace-hub/workflow-gatepass/SKILL.md`
- `.claude/skills/workspace-hub/work-queue-workflow/SKILL.md`
- `scripts/work-queue/build-session-gate-analysis.py`
- `scripts/work-queue/audit-session-signal-coverage.py`
- `scripts/work-queue/log-gate-event.sh`
- `scripts/agents/session.sh`, `scripts/agents/work.sh`, `scripts/agents/plan.sh`,
  `scripts/agents/execute.sh`, `scripts/agents/review.sh`
