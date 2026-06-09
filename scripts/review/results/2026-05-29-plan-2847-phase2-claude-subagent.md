# Plan-stage adversarial review — #2847 Phase 2 (auto-promotion)

> **Stage:** plan · **Issue:** [#2847](https://github.com/vamseeachanta/workspace-hub/issues/2847) Phase 2 · **Date:** 2026-05-29 · **Complexity:** T3
> **Plan:** docs/plans/2026-05-29-issue-2847-phase2-auto-promotion.md

## Method
Independent fresh-context subagent (cross-provider unavailable from a Claude-Code session; degraded T3→1 — Codex pass strongly recommended before implementing this highest-stakes slice). All load-bearing findings empirically verified by the main session against the merged 1a/1b code.

## Round 1 verdict: CHANGES REQUIRED

| # | Sev | Finding | Verified |
|---|-----|---------|----------|
| 1 | CRITICAL | auto-promote safety depends on `enforce_leader_fence` (separate, default-OFF flag); `is_leader_machine` is hostname/token-only (no git state), so fence-off ⇒ old leader keeps originating ⇒ split-brain in the DEFAULT config. "No split-brain by construction" was false. | ✅ read is_leader_machine L107 + run_loop L377/L405 |
| 2 | MAJOR | abort-on-term-moved depends on "heartbeat preserves term" (lives in may_write_leases) — load-bearing, untested as an invariant | ✅ may_write_leases uses st.term |
| 3 | MAJOR | leases are local-disk-only + machine-scoped key → new leader can't see dead leader's in-flight leases → redistribution double-dispatch | ✅ idempotency_key = issue:provider:machine |
| 4 | MAJOR | threaded race test risks false pass (shared store / git lock) | sound |
| 5 | MEDIUM | `observed` param = stale-TOCTOU surface; should derive from own read | sound |
| 6 | MEDIUM | old-leader mid-tick origination window unbounded (run_loop gates once/tick, not per-append) | ✅ run_loop structure |
| 7 | MEDIUM | plan falsely marked "adversarial-reviewed" + referenced a non-existent artifact; ABORTED-post-push cleanup unclear | ✅ |
| 8 | MINOR | no queue parser in Files; prev_leader TOCTOU | ✅ |

## Resolution (revision)
- **#1 (headline):** fence is now a HARD PRECONDITION — `try_promote` returns `FENCE_REQUIRED` + alerts unless `leader_fence_enabled_from_env()`; 2 ACs + tests (`test_promote_refused_when_fence_disabled`, `test_old_leader_NOT_demoted_when_fence_off`); enable-runbook documents fence-first ordering. With the fence on, the committed term is the authority and the old leader self-demotes.
- **#2:** added `test_heartbeat_preserves_term_invariant`.
- **#3:** re-route uses machine-independent idempotency (`issue:provider`) + a GitHub wip marker; only live-`gh` open+unclaimed re-routes; `test_redistribute_no_double_dispatch_across_machines`.
- **#4:** spec → separate subprocess clones + barrier post-read/pre-push; assert exactly one PUSHED + rest REJECTED (≠ PUSH_FAILED) + origin term +1.
- **#5:** dropped `observed`; CAS vs `_last_read_sha` is the guard.
- **#6:** bounded (≤ max_implementation_per_run/promotion) + documented; named the per-append follow-on.
- **#7:** status corrected; this artifact written; ABORTED-post-push clarified (ref owned by superseder → no orphan).
- **#8:** `_read_queue` added to Files; `prev_leader` from same read.

## Result
**PASS after revision** — the CAS-promotion core is sound and the CRITICAL fence-coupling is now structural + tested. Strong recommendation: obtain a **Codex cross-review of this plan AND the 1a/1b foundation** before implementation (T3 wants 3 providers; this session has been Claude-subagent-only), given it changes live multi-machine leadership.
