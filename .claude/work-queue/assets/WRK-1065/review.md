# WRK-1065 Cross-Review — Plan Stage (Stage 6)

## Codex Verdict: MAJOR

### Findings

- **P1 (MAJOR)**: No live context-usage hook signal exists. `--usage-pct` has no concrete caller.
  **Resolution**: Reframe as pure callable utility; document manual/adapter invocation contract.
  Script will NOT auto-fire from a hook; it is invoked explicitly by the operator or a wrapper.

- **P2**: Threshold inconsistency — title says 80%, body/ACs say 80%.
  **Resolution**: Standardize to 80% everywhere; update WRK title.

- **P2**: `/wrk-resume` referenced as resume path; it is now diagnostic-only.
  **Resolution**: Session-chunking.md and Stage 10 note will reference `/work run WRK-NNN` as primary.

- **P3**: Missing edge-case tests (no active WRK, duplicate 80% calls, checkpoint.sh failure).
  **Resolution**: Add these to test plan.

### Updated Plan

1. `scripts/hooks/context-monitor.sh` — callable utility; accepts `--usage-pct <N>`;
   logs structured WARNING at 70%, checkpoints at 80% (calls checkpoint.sh + writes
   context-warning.yaml); idempotent (skip if already warned at same threshold this session);
   exits 0 when no active WRK (logs SKIP).
2. `.claude/docs/session-chunking.md` — when to chunk; break points; resume via `/work run WRK-NNN`
3. Edit Stage 10 in work-queue-workflow/SKILL.md — budget note + pointer to session-chunking.md
4. `tests/hooks/test-context-monitor.sh` — covers: 70% only, 80% + checkpoint, no-active-wrk,
   duplicate 80%, checkpoint failure propagation

### Disposition
All P1/P2 addressed in plan before implementation. P3 expanded in test list.
