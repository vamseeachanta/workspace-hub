# Plan-stage adversarial review — #2847 multi-machine leader failover

> **Stage:** plan · **Issue:** [#2847](https://github.com/vamseeachanta/workspace-hub/issues/2847) · **Date:** 2026-05-28 · **Complexity:** T3
> **Plan:** docs/plans/2026-05-28-issue-2847-leader-failover.md

## Method / provenance
Cross-provider Codex/Gemini dispatch is unavailable from a Claude-Code session (`CLAUDECODE=1` trips `submit-to-codex`; Gemini trust-folder gate). Per the documented fallback, plan-stage review was performed by an **independent fresh-context subagent** prompted to attack the design (distributed-systems failure modes) and default to non-APPROVE. Every load-bearing finding was **empirically verified by the main session against the live code** before the plan was revised (per `feedback_verify_subagent_firewall_claims`). T3 nominally wants 3 providers — this is a **degraded T3→1** pass; the user is advised to add Codex/Gemini review out-of-session before implementation.

## Round 1 verdict: CHANGES REQUIRED — 3 BLOCKER, 3 MAJOR, 4 MINOR

| # | Sev | Finding | Verified |
|---|-----|---------|----------|
| 1 | BLOCKER | `dispatch.py:52` hardcodes `dispatch_status: ready`; all 1489 committed queue cards are `ready`, none `running` → original "flag running / reroute ready" safety is dead code → double-execution risk | ✅ grep |
| 2 | BLOCKER | git push-race fences the state-file token, not execution (local flock + local `leases.jsonl`); an alive-but-cannot-push leader keeps writing local leases while a secondary promotes → split-brain | ✅ sound |
| 3 | BLOCKER | `run_loop` is one tick (L342); `append_lease` (L373/L392) has no term re-check → fencing has no insertion point | ✅ grep |
| 4 | MAJOR | winning push necessary-not-sufficient; auto-sync silent-pusher could let a rejected loser re-land via rebase | — |
| 5 | MAJOR | cross-machine lease double-count: idempotency key `issue:provider:machine` doesn't collide across machines; 3h TTL doesn't protect | ✅ L201 |
| 6 | MAJOR | the safety-critical CAS was unit-mocked only → never actually tested | — |
| 7 | MINOR | revive-during-redistribution window | — |
| 8 | MINOR | `is_leader_machine` L109 true for any `promotion_token` → unfenced second promotion door | ✅ grep |
| 9 | MINOR | no term-monotonicity/corruption guard; no leader-side self-alert on push failure; heartbeat-storage undecided | — |
| 10 | NIT | "within one cycle" untestable without a pinned cron period | — |

## Revisions applied to the plan
- **Two-phase restructure**: Phase 1 = safe alert-only + the self-fencing invariant (no auto-promotion); Phase 2 = auto-promotion behind an opt-in flag.
- **BLOCKER 2 (load-bearing):** the right to write leases now requires a **recently-confirmed git push** (`may_write_leases`), not merely holding the local flock — a leader that cannot push self-fences. This is what actually prevents split-brain.
- **BLOCKER 1:** redistribution is **flag-only by default for ALL orphaned cards**; auto re-route only on a positive freshness proof re-derived from live `gh` state at action time, never from the queue snapshot.
- **BLOCKER 3:** every `append_lease` call site (L373/L392) gated on `may_write_leases` (term + confirmed-push), not a once-per-`main()` check.
- **MAJOR 4:** post-push confirmation (re-pull, assert `leader==me && term==mine`); rejected push ⇒ stand down, never `pull --rebase && push`.
- **MAJOR 6:** added a **real-git integration test** (bare origin + 2 clones) proving exactly-one-winner and that the loser doesn't re-land via rebase.
- **MINOR 7-10:** live-`gh` redistribution targets; `promotion_token` routed through the term/state fence; term-regression corruption guard + leader self-alert/self-demote; cron period pinned; heartbeat storage decided (dedicated path + amend).

## Result
**PASS after revision** for the purpose of presenting to the user for approval. The phase-structure and self-fence invariant address the BLOCKERs at the design level. Recommend (a) a second adversarial pass on the revised plan and (b) Codex/Gemini cross-review out-of-session before implementation, given this is a T3 distributed-systems change.
