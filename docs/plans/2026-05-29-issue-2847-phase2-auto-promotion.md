# Plan for #2847 Phase 2: auto-promotion + orphaned-work redistribution

> **Status:** plan-review, CHANGES REQUIRED after 2026-06-09 Codex adversarial review. This artifact is retained as the recovered Phase 2 draft; implementation is blocked until a repaired Phase 2 plan is reviewed and explicitly approved. Agent does not self-approve.
> **Complexity:** T3 (highest-stakes slice — changes live leadership)
> **Date:** 2026-05-29
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2847
> **Client:** N/A
> **Review artifacts:** scripts/review/results/2026-05-29-plan-2847-phase2-claude-subagent.md; scripts/review/results/2026-06-09-plan-2847-phase2-codex.md
> **Parent design:** docs/plans/2026-05-28-issue-2847-leader-failover.md (the umbrella plan; this details its Phase 2)

---

## Resource Intelligence Summary

### Existing repo code (on main, post-1a/1b)
- Found: `scripts/ai/dispatch_leader.py` — `LeaderState`; `ClaimResult{PUSHED,REJECTED,PUSH_FAILED}`; `Status{LEADER,OK,STALE,UNDETERMINED}`; `GitLeaderStateStore` (dedicated-ref store: `read`=fetch+show setting `_last_read_sha`; `claim`=`commit-tree` + `--force-with-lease` CAS against the last-read SHA); `may_write_leases` (self-fence — confirmed-push); `leader_can_originate`; `check` (detect + **ALERT only**, UNDETERMINED on inconclusive). **The atomic CAS Phase 2 needs is already built + tested** (push-race exactly-one-winner; no-brick regression).
- Found: `scripts/cron/dispatch-leader-watch.sh` — leader `--heartbeat`; secondary `--check` (alert only, exit 2 on STALE).
- Found: `scripts/ai/provider-dispatch-loop.py` — `run_loop` gates origination on `leader_can_originate` when `enforce_leader_fence` (env `DISPATCH_ENFORCE_LEADER_FENCE`, default off). `make_lease`, `select_execution_ready`, the per-machine queue model.
- Found: `.claude/dispatch/<machine>.yaml` — git-tracked per-machine queues; `dispatch.py:52` hardcodes `dispatch_status: ready` (so the queue is **NOT** a reliable in-flight signal — Phase 2 redistribution must not trust it; verified in the umbrella plan's review).
- **Gap (this plan builds):** no `try_promote` (auto-promotion), no `redistribute`, the watcher's auto-promote path, and the returning-old-leader fencing wired end-to-end.

### Documents consulted
- Umbrella plan `docs/plans/2026-05-28-issue-2847-leader-failover.md` — Phase 2 design sketch (push-race CAS + post-push confirm + flag-only/live-gh redistribution + real-git integration test).
- Phase 1a/1b review artifacts — the CAS is server-side atomic; redistribution must use live `gh` (queue `dispatch_status` is hardcoded `ready`); per-tick push aligns with cron cadence.
- Memory `feedback_autosync_silent_pusher` / `feedback_reflog_as_ground_truth` — promotion must NOT `pull --rebase && push` on a rejected claim (the loser must stand down).

### Evidence (embedded)
- `grep 'def try_promote\|def redistribute' dispatch_leader.py` → 0 (to build).
- `grep -c 'dispatch_status: ready' .claude/dispatch/*.yaml` (umbrella plan) → all `ready` → queue not in-flight-authoritative.
- Building blocks present (verified 2026-05-29): ClaimResult, Status, check, leader_can_originate, may_write_leases, GitLeaderStateStore.

*Distinct sources: 5 (umbrella plan + 1a/1b reviews + dispatch_leader + watcher + queue/dispatch.py).*

---

## Deliverable
Opt-in **auto-promotion** (env `DISPATCH_ENABLE_AUTO_PROMOTE`, default OFF): when a secondary detects a stale leader, it atomically promotes itself via the existing dedicated-ref CAS (`term+1`, post-push confirmed), then **flags** orphaned work (re-routing only what live `gh` state proves is safe). Review/merge/gated work is never auto-failed-over. All under TDD incl. a **concurrent real-git promotion-race** test (separate subprocess clones).

## 2026-06-09 Recovery Review: Implementation Blocked

This plan branch was recovered after Phase 1a/1b merged. The detailed Phase 2 plan was never merged to `main`, and the merged approval marker explicitly scoped the prior approval to Phase 1 first. A fresh Codex adversarial review on 2026-06-09 found that implementation should not proceed from this draft.

The repaired plan must address, before implementation:

- an explicit Phase 2 approval record, separate from the Phase 1 approval marker;
- a decision on how this leader-failover design will integrate with, replace, or stay separate from the newer `scripts/operations/dispatch_lease.py` and `scripts/operations/git_ref_lease.py` CAS + fencing-token lease surface;
- an enforceable cluster-wide fence-readiness gate, not only a local `DISPATCH_ENFORCE_LEADER_FENCE` assertion;
- per-append fencing before auto-promotion, or a documented acceptance of bounded duplicates;
- a concrete change to the live idempotency contract or an alternate cross-machine WIP acquisition guard;
- redistribution restricted to live-eligible and route-eligible work, not the full machine backlog;
- watcher shell/CLI tests for stale/fresh/undetermined plus auto-promote/fence env combinations;
- legal/security gate coverage in acceptance.

See `scripts/review/results/2026-06-09-plan-2847-phase2-codex.md`.

### CRITICAL precondition (review r1 #1): auto-promote REQUIRES the leader fence
The old leader's origination is gated by `is_leader_machine` (hostname/token, **git-state-blind**) UNLESS `enforce_leader_fence` is on (the only gate that reads the committed term via `leader_can_originate`). So a secondary promoting to `term+1` only causes the old leader to **self-demote** if the old leader runs with `DISPATCH_ENFORCE_LEADER_FENCE=1`. With the fence off (the default), promoting a secondary yields **TWO originating leaders** — split-brain. Therefore:
- `try_promote` and the watcher's auto-promote path **refuse to run (no-op + ALERT) unless `leader_fence_enabled_from_env()` is true.** Auto-promote is inert without the fence — a hard precondition, tested.
- Operational contract: enabling auto-promote on the cluster REQUIRES the fence enabled on every dispatch-capable machine first. Documented in the enable runbook.
With the fence on, `is_leader_machine` (hostname) is necessary-but-not-sufficient; the committed `term` is the authority, so the old leader passes the hostname check but fails `leader_can_originate` (superseded term) and self-demotes. That is what makes "no split-brain" true — and it is now structurally enforced, not assumed.

---

## Pseudocode

```
class PromotionResult(Enum): PROMOTED, LOST, ABORTED, FAILED, FENCE_REQUIRED

def try_promote(store, machine, *, now=None, fence_enabled=None, alert=None) -> PromotionResult:
    # PRECONDITION (review #1): refuse to promote unless the leader fence is active
    # cluster-wide — otherwise the old leader keeps originating on hostname alone.
    if not (fence_enabled if fence_enabled is not None else leader_fence_enabled_from_env()):
        alert("auto-promote refused: DISPATCH_ENFORCE_LEADER_FENCE must be enabled first"); return FENCE_REQUIRED
    st = store.read()                                  # the ONLY source of truth (no stale `observed`; review #5)
    prev_leader = st.leader                            # captured from THIS read (review #8)
    if st.leader == machine: return PROMOTED           # already leader (idempotent)
    if (now - st.heartbeat) <= STALE_THRESHOLD_S: return ABORTED   # leader revived
    base_term = st.term
    res = store.claim(LeaderState(machine, base_term + 1, now, pid))  # CAS vs _last_read_sha (force-with-lease)
    if res == REJECTED: alert("promotion lost to peer"); return LOST   # stand down — NEVER pull --rebase && push
    if res != PUSHED:   alert("promotion push failed"); return FAILED
    confirm = store.read()                             # winning push is necessary-not-sufficient
    if not (confirm.leader == machine and confirm.term == base_term + 1):
        # We landed term+1 but a 3rd machine immediately superseded us (ref now theirs,
        # not ours) -> we are NOT leader; abort cleanly. No orphan: the ref is owned by
        # whoever's commit is latest; we never act as leader, so nothing to clean up.
        alert("promotion superseded immediately"); return ABORTED
    return (PROMOTED, prev_leader)

def redistribute(dead_leader, *, gh_state, route, alert) -> dict:
    # Queue dispatch_status is hardcoded 'ready' AND leases.jsonl is local-disk-only, so
    # the new leader CANNOT see the dead leader's in-flight leases (machine-scoped key,
    # not cross-machine). The ONLY cross-machine in-flight signal is GitHub itself.
    out = {"rerouted": [], "flagged": []}
    for card in read_queue(f".claude/dispatch/{dead_leader}.yaml").cards:
        live = gh_state(card.gh)                        # authoritative cross-machine state AT ACTION TIME
        # Re-route ONLY if GitHub proves the issue is open, unclaimed (no wip label /
        # assignee / in-progress), and not gated. Anything else -> FLAG (never auto-run).
        if live.open and live.unclaimed and not live.gated:
            # Cross-machine idempotency (review #3): re-derive the lease key as issue:provider
            # (machine-INDEPENDENT) for redistributed work, and stamp a GitHub wip marker so a
            # revived dead leader's local key collision is not the only guard.
            route(card, idempotency="issue:provider", mark_wip_on_github=True)
            out["rerouted"].append(card)
        else:
            flag(card, f"orphaned by dead leader {dead_leader}; needs human/gate")
            out["flagged"].append(card)
    return out                                          # review/merge/gated/claimed -> flagged, never auto-run

# watcher (secondary): --check path, auto-promote behind BOTH the auto-promote flag AND the fence
status = check(store, machine, alert=...)               # check() sets store._last_read_sha
if status == STALE and AUTO_PROMOTE_ENABLED:            # AUTO_PROMOTE_ENABLED also requires fence (see try_promote)
    result = try_promote(store, machine, now=now, alert=...)
    if result is PROMOTED: redistribute(dead_leader=result.prev_leader, gh_state=gh, route=route, alert=...)
```

Returning old leader fencing (only valid because the fence precondition above is enforced):
`may_write_leases`/`leader_can_originate` return False when `st.term > my_term`; once a secondary commits `term+1`, the fenced old leader's next tick reads the higher term and self-demotes. **This is inert without the fence** — hence the hard precondition. Phase 2 adds an end-to-end test under BOTH fence-on (self-demotes) and fence-off (promotion refused).

---

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Modify | scripts/ai/dispatch_leader.py | add `PromotionResult` (incl. `FENCE_REQUIRED`), `try_promote` (fence-precondition + CAS + post-confirm + no-rebase, derives all state from its own read), `redistribute` (flag-only/live-gh + machine-independent idempotency for re-routed work), a small `_read_queue(path)` YAML parser (one does not exist), and an injectable `gh_state` accessor; CLI `--promote` (guarded by BOTH env flags) |
| Modify | scripts/cron/dispatch-leader-watch.sh | secondary `--check`: on STALE + `DISPATCH_ENABLE_AUTO_PROMOTE` (which itself requires the fence), attempt promote then redistribute; log outcome incl. `FENCE_REQUIRED` refusal |
| Modify | scripts/ai/provider-dispatch-loop.py | (minor) surface promoted-leader term so `enforce_leader_fence` path reflects new leadership; no behavior change when flags off |
| Modify | tests/ai/test_dispatch_leader.py | unit: try_promote (won/lost/aborted-revived/aborted-term-moved/failed); redistribute flag-only vs reroute on live-gh; returning-old-leader self-demotes |
| Create | tests/ai/test_dispatch_leader_promotion_race.py | **concurrent real-git** promotion race (threads/forks, bare origin + N clones) → exactly one PROMOTED, rest LOST; origin term advances by exactly 1 |
| Update | docs/plans/README.md | index |

---

## TDD Test List
| Test | Verifies | Phase |
|---|---|---|
| **test_promote_refused_when_fence_disabled** | fence env off → FENCE_REQUIRED, no claim (review #1 precondition) | unit |
| test_promote_won_when_stale_fence_on | fence on + stale + CAS PUSHED + confirm → PROMOTED (term+1) | unit |
| test_promote_lost_on_rejected_no_rebase | claim REJECTED → LOST, stands down, NO second attempt/rebase | unit |
| test_promote_aborts_when_leader_revived | re-read heartbeat fresh → ABORTED (no claim) | unit |
| test_promote_aborts_when_push_lands_but_state_not_mine | PUSHED but confirm read mismatches (superseded) → ABORTED | unit |
| **test_heartbeat_preserves_term_invariant** | may_write_leases heartbeat keeps st.term (load-bearing for abort logic; review #2) | unit |
| test_returning_old_leader_self_demotes_when_fenced | fence on: after term+1, old leader leader_can_originate → False | unit |
| **test_old_leader_NOT_demoted_when_fence_off** | fence off: old leader still originates → proves the precondition is necessary (review #1) | unit |
| test_redistribute_flags_inflight_uses_live_gh | live wip/in-progress/gated/closed → flagged, never rerouted | unit |
| test_redistribute_reroutes_only_open_unclaimed | live open+unclaimed → rerouted with machine-independent key | unit |
| **test_redistribute_no_double_dispatch_across_machines** | card the dead leader already leased (different machine) → not re-run (review #3) | unit |
| **test_promotion_race_exactly_one_winner_concurrent** | N **subprocess clones**, barrier post-read/pre-push, all push term+1 to one bare origin → exactly one PUSHED, rest REJECTED (distinct from PUSH_FAILED); origin term == base+1 | integration |
| test_end_to_end_no_double_origination_under_fence | fence on both: promoted secondary originates, demoted old leader does not | integration |

---

## Acceptance Criteria
- [ ] `uv run pytest tests/ai/test_dispatch_leader.py tests/ai/test_dispatch_leader_promotion_race.py tests/ai/test_provider_dispatch_loop.py -v` green; no regression in the existing 41.
- [ ] **Fence precondition (review #1):** auto-promote is INERT unless `DISPATCH_ENFORCE_LEADER_FENCE` is enabled; a machine with auto-promote on + fence off **refuses to promote and alerts** (`FENCE_REQUIRED`). Proven by `test_promote_refused_when_fence_disabled` AND `test_old_leader_NOT_demoted_when_fence_off`.
- [ ] **No split-brain end-to-end (proven):** with the fence on cluster-wide — concurrent promotion → exactly one PROMOTED (origin term +1, losers REJECTED, no rebase); the demoted old leader cannot originate (`test_end_to_end_no_double_origination_under_fence`).
- [ ] **No cross-machine double-dispatch:** redistribution flags in-flight/gated/claimed work and re-routes ONLY live-`gh`-proven open+unclaimed cards with a machine-independent idempotency key (never trusts the hardcoded `dispatch_status` or the local-only lease ledger).
- [ ] Auto-promotion is **opt-in** (`DISPATCH_ENABLE_AUTO_PROMOTE`, default off); with it off, the watcher remains alert-only (Phase 1 behavior unchanged).
- [ ] Mid-tick window is bounded + documented (≤ `max_implementation_per_run` duplicate leases per promotion event, cleared next tick) — see Risks.
- [ ] `bash -n` clean; review artifact posted; enable-runbook documents fence-first ordering.

---

## Adversarial Review Summary

Plan-stage review by an independent fresh-context subagent (cross-provider unavailable from a Claude-Code session; degraded T3→1 — a Codex pass is **strongly recommended** before implementing this highest-stakes slice). All load-bearing findings main-verified against live code.

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (subagent, r1) | CHANGES REQUIRED | 1 CRITICAL + 3 MAJOR + 3 MEDIUM/MINOR (below) |

**Verified findings + resolution (this revision):**
- **CRITICAL #1 (verified)** — auto-promote's safety silently depended on `enforce_leader_fence`, a *separate default-off flag*; `is_leader_machine` is hostname/token-only (no git state), so with the fence off the old leader keeps originating → split-brain in the DEFAULT config. → Made the fence a **hard precondition** (`try_promote` returns `FENCE_REQUIRED` + alerts if the fence is off); added 2 ACs + tests (`test_promote_refused_when_fence_disabled`, `test_old_leader_NOT_demoted_when_fence_off`); documented fence-first enable runbook.
- **MAJOR #2** — abort logic depends on "heartbeat preserves term" (true today, in another function). → added `test_heartbeat_preserves_term_invariant`.
- **MAJOR #3** — leases are local-disk-only + machine-scoped key, so the new leader can't see the dead leader's in-flight leases; redistribution could double-dispatch. → re-route uses machine-independent idempotency + a GitHub wip marker; only live-`gh` open+unclaimed re-routes; added `test_redistribute_no_double_dispatch_across_machines`.
- **MAJOR #4** — threaded race test risks a false pass (shared store/git lock). → spec changed to **separate subprocess clones + barrier post-read/pre-push**, assert exactly one PUSHED + rest REJECTED (distinct from PUSH_FAILED) + origin term +1.
- **MEDIUM #5** — `observed` param was a stale-TOCTOU surface. → dropped; `try_promote` derives everything from its own read; the CAS (force-with-lease vs `_last_read_sha`) is the real guard.
- **MEDIUM #6** — old-leader mid-tick origination window unbounded. → bounded + documented (≤ `max_implementation_per_run` per promotion; see Risks); named the per-append-vs-per-tick gap inherited from 1b.
- **MEDIUM #7** — plan falsely marked "adversarial-reviewed" with a missing artifact + ABORTED-cleanup unclear. → status corrected; this artifact written; ABORTED-post-push clarified (ref owned by the superseder → no orphan).
- **MINOR #8** — no queue parser in Files; `prev_leader` TOCTOU. → `_read_queue` added to Files; `prev_leader` captured from the same read.

**Overall result:** PASS after revision (the CRITICAL fence-coupling is now structural + tested). Recommend a Codex pass before implementation.

---

## Risks and Open Questions
- **Risk — redistribution double-execution:** the only safe signal is live `gh` at action time; the git queue's `dispatch_status` is hardcoded `ready`. Plan flags everything not provably-safe. The `gh_state` accessor must be injectable for tests (no network in unit tests).
- **Risk — promotion + the 1b fence interaction:** after promotion, the new leader's `enforce_leader_fence` path sees itself as leader (it reads the ref it just wrote). The old leader self-demotes before its next origination via the term check — but ONLY when the fence is on (the CRITICAL precondition above). End-to-end test under fence-on AND fence-off.
- **Risk — mid-tick origination window (review #6):** `run_loop` checks the fence ONCE per tick, then writes up to `max_implementation_per_run` (default 3) leases. If a secondary promotes mid-tick, the old leader's already-started batch completes before its NEXT tick self-demotes. Bound: **≤ `max_implementation_per_run` duplicate leases per promotion event**, cleared the next tick. This inherits the Phase-1b per-tick (not per-append) gate granularity. If unacceptable, a follow-on gates each `append_lease` on `may_write_leases` (per the module docstring's "call immediately before every lease append"); the redistribution idempotency (machine-independent key) also bounds the blast radius. Decide at approval.
- **Risk — concurrent test flakiness:** the threaded real-git test must serialize via the actual git CAS, not test timing. Use a barrier so all threads claim from the same base; assert on the set of results, not order.
- **Open:** auto-promote default OFF + opt-in (recommended, given live-leadership stakes) vs on-by-default once validated? Recommend OFF; flip per-machine after soak.
- **Open:** should a promotion open/annotate a GitHub issue for operator visibility (the umbrella's "surface" AC)? Recommend a one-line rolling note via the #2841 Phase-C consistency check rather than a new issue per promotion.
- **Strong recommendation:** given this changes live leadership, obtain a **Codex cross-review** of this plan AND of the 1a/1b foundation before implementation (T3 wants 3 providers; this session's reviews were Claude-subagent-only).

## Complexity: T3
Changes live multi-machine leadership; concurrent correctness; multi-file. Cross-review T3=3 providers ideally; cross-provider dispatch unavailable from a Claude-Code session → fresh-context subagent fallback (degraded), Codex pass strongly recommended out-of-session.
