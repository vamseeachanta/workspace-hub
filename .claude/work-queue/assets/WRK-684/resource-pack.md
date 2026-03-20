# Resource Pack: WRK-684

## Problem Context
The `comprehensive-learning` skill synthesizes knowledge and trends across sessions, but its outputs (stored in `.claude/state/learning-reports/`) are currently siloed from the daily productivity report produced by `/today`. To close the loop, we need to define standardized outcomes from the learning pipeline and ensure they roll up into the daily summary.

## Relevant Documents/Data
- `.claude/skills/workspace-hub/comprehensive-learning/SKILL.md`: Pipeline definition.
- `scripts/productivity/daily_today.sh`: The `/today` report orchestrator.
- `scripts/productivity/sections/session-analysis.sh`: Current logic for session metrics.
- `.claude/state/learning-reports/`: Target source for roll-up outcomes.

## Constraints
- Must not add significant latency to the `/today` command.
- Should handle cases where the nightly learning run hasn't occurred yet (graceful fallback).
- Data must be scannable and actionable.

## Assumptions
- Learning reports follow the Markdown format defined in Phase 10 of `comprehensive-learning`.
- dev-primary is the primary machine for generating these reports.

## Open Questions
- Should we create a new `/today` section (`learning-outcomes.sh`) or merge it into `session-analysis.sh`?
- What specific outcomes are most valuable? (e.g., "Knowledge Verified", "Blocked Trends", "Action Candidates").

## Domain Notes
- This is an integration task to improve institutional memory and daily awareness of system-driven improvements.
