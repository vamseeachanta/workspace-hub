# Code Review — #2841 Phase C — Claude (fresh-context subagent)
- Date: 2026-05-29 · Stage: code (adversarial), commit 1ca1fa584 · Verdict: MINOR (no blockers) → robustness fixes applied
- Codex/Gemini UNAVAILABLE (CLAUDECODE, #2721/#2715) — single-author+fresh-context fallback.

## Reviewer confirmed CORRECT: rolling-issue upsert (empty/multi/TOCTOU), label idempotency, find-absence→stale, matrix-always + unconditional exit-1-on-drift, schedule renders via setup-cron, exit codes.

## Findings (fixes applied)
- F7 [LOW, real]: CONSISTENCY_SELFTEST_FAILS seam could neuter a real run if leaked. FIXED: gated on explicit CONSISTENCY_SELFTEST=1 marker; test asserts seam is INERT without it.
- F3: ${HOME} unguarded under set -u → ${HOME:-/nonexistent} (deadletter check degrades to PASS, no crash).
- F6: schedule 0 6 * * 0 collided with daily 06:00 jobs → 15 6 * * 0 (offset).
- F8 test gaps: +2 tests (label-already-exists → no create; seam-inert-without-marker).

## Accepted / not-fixed (non-blocking): two-open-issues no self-heal (dev-primary-only + edit-newest is acceptable); requires:[gh] is advisory (setup-cron doesn't enforce); run_checks real-path coverage bypassed by seam (system-state dependent — test seam is the deliberate tradeoff). F3 follow-on (skill-index couples SOUL-drift to live skills) noted on PR for a future refinement.
