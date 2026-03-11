# WRK-1095 Cross-Review — Claude (Phase 1, Plan)

## Verdict: MINOR

### Finding F1 — MINOR
pre-push.sh needs `COMPLEXITY_RATCHET_GATE=1` opt-in guard.
Matches existing `MYPY_RATCHET_GATE=1` pattern at line 198.
**Resolution:** Incorporated into plan Step 5.

### Finding F2 — MINOR
6th TDD test required: `test_bypass_reason_logged` for `SKIP_COMPLEXITY_REASON` audit path.
Critical path per testing.md — bypass audit must be verified by tests.
**Resolution:** Incorporated into plan Step 6.

### Informational (non-blocking)
- `avg_cc` in baseline is informational only; clarify in code comments.
- `--complexity-ratchet` in check-all.sh: run once (aggregate), not per-repo.

Both MINOR findings incorporated into plan before Stage 10 implementation begins.
