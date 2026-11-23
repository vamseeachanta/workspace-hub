# Plan for #2847: multi-machine dispatch leader failover — auto-promote/redistribute when the coordinator host is down

> **Status:** plan-review (adversarial-reviewed; awaiting USER approval — agent does not self-approve)
> **Complexity:** T3
> **Date:** 2026-05-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2847
> **Client:** N/A
> **Review artifacts:** scripts/review/results/2026-05-28-plan-2847-claude-subagent.md (+ codex/gemini if dispatch becomes available)

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/ai/provider-dispatch-loop.py` — the dispatch loop. `acquire_leader_lock()` (≈L143) uses `fcntl.flock` on `logs/ai-provider-dispatch/leader.lock`; `is_leader_machine()` (≈L107) returns true iff `machine == cfg.leader_host` (default `ace-linux-1`) **or** `promotion_token` is set; `coexistence_preflight()` (≈L112) checks the local `competing-dispatcher.marker`; lease ledger (`leases.jsonl`) is append-only with a 3 h TTL (`DEFAULT_LEASE_TTL_S`), `expire_stale_leases()` derives `stale` state but performs **no redistribution**.
- Found: `scripts/dispatch/dispatch.py` — writes the per-machine queue files `.claude/dispatch/<machine>.yaml` (git-tracked); pull-based consumption by each machine's session.
- Found: `scripts/monitoring/agents-board.sh` — liveness via **process table only** (PID `kill -0`, `pgrep`); LOCAL to the host running it — cannot observe a remote machine.
- Found: `config/workstations/registry.yaml` — canonical machine identity/capability registry (`dev-primary`=ace-linux-1 leader, `dev-secondary`=ace-linux-2 worker).
- Found: `tests/ai/test_provider_dispatch_loop.py` — pytest, 11 tests; patterns: `DISPATCHER_MACHINE` env override, `tmp_path`, `dry_run`, dataclass fixtures. This is the test idiom to mirror.
- **Gap:** no cross-machine coordination primitive exists. `leader.lock`, `leases.jsonl`, `competing-dispatcher.marker` are all under `logs/` which is **gitignored** (`.gitignore:98 logs/*`) and on local disk (not NFS) — i.e. per-machine. `fcntl.flock` is a same-host kernel lock. Leadership is enforced only by **config** (`leader_host=ace-linux-1`), not by any shared lock.
- **Gap:** no auto-promotion (manual `--promotion-token` only, and the token is not validated), no lease redistribution, no machine-level heartbeat, and the dispatch loop is **not** in `schedule-tasks.yaml` (manual/Hermes-invoked).

### Standards
Not applicable (harness/infrastructure issue).

### LLM Wiki pages consulted
No relevant wiki pages (infrastructure, not domain knowledge).

### Documents consulted
- Issue #2847 (body) — feature spec, fix directions, acceptance criteria; explicitly scopes this as **machine-level** failover, distinct from #2841's lane-level failover.
- Issue #2841 — Decision #3 (hybrid posture: auto-failover throughput work, keep manual gates for review/merge). Parent.
- Issue #2519 — coexistence/split-brain preflight; the anchor for split-brain prevention.
- `config/scheduled-tasks/schedule-tasks.yaml` — per-machine `schedule_variant` cron model; where the watcher cron will be declared.
- Memory `feedback_cross_machine_execution` — established principle: "per-machine tasks via shared git repo, not SSH/rsync." Drives the git-substrate decision.
- Memory `feedback_autosync_silent_pusher` / `feedback_reflog_as_ground_truth` — push-race handling; the promotion design depends on `[rejected]` being observable.

### Gaps identified
1. No cross-machine leadership substrate (must build — git-tracked leader-state file).
2. No remote-leader liveness signal (must build — committed heartbeat + staleness threshold).
3. No atomic promotion / split-brain guard across hosts (must build — git push-race + fencing term).
4. No redistribution or flagging of orphaned work on leader death (must build — operate on git-visible queue state).
5. No scheduled watcher to run detection within a bounded cycle (must build — per-secondary cron).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-28 via `gh issue view`):
- `#2847` — OPEN — feat(dispatch): multi-machine leader failover
- `#2841` — OPEN — orchestrator consistency umbrella (parent, Decision #3)
- `#2519` — referenced — coexistence preflight anchor

**File existence** (`git ls-files` / `ls`, 2026-05-28):
- EXISTS: scripts/ai/provider-dispatch-loop.py
- EXISTS: scripts/dispatch/dispatch.py
- EXISTS: scripts/monitoring/agents-board.sh
- EXISTS: config/workstations/registry.yaml
- EXISTS: tests/ai/test_provider_dispatch_loop.py
- EXISTS (git-tracked, 7 files): .claude/dispatch/<machine>.yaml
- MISSING (new — this plan creates): scripts/ai/dispatch_leader.py, scripts/cron/dispatch-leader-watch.sh, .claude/dispatch/_leader-state.yaml, tests/ai/test_dispatch_leader.py

**Gap proofs:**
- `git check-ignore -v logs/ai-provider-dispatch/leader.lock` → `.gitignore:98:logs/*` → leader lock is NOT shared cross-machine.
- `git ls-files logs/ai-provider-dispatch/` → 0 files → lease/lock/marker are local-only.
- `df -T /mnt/local-analysis/workspace-hub` → `/dev/sdc1 fuseblk` (local) → no NFS sharing.

**Reproduction proofs:** N/A — feature request (no alleged runtime failure to reproduce). The "silent halt on dead leader" is a design gap, demonstrated by the gap proofs above (no cross-machine primitive exists), not a failing test.

*Distinct sources consulted: 6 (issue body + provider-dispatch-loop.py + dispatch.py/queues + registry.yaml + #2841/#2519 + cross-machine memory).* 

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-05-28-issue-2847-leader-failover.md |
| Implementation (core) | scripts/ai/dispatch_leader.py |
| Watcher cron | scripts/cron/dispatch-leader-watch.sh |
| Leadership state (git-tracked seed) | .claude/dispatch/_leader-state.yaml |
| Loop integration | scripts/ai/provider-dispatch-loop.py (modify) |
| Board panel | scripts/monitoring/agents-board.sh (modify) |
| Schedule | config/scheduled-tasks/schedule-tasks.yaml (modify) |
| Tests | tests/ai/test_dispatch_leader.py |
| Plan review | scripts/review/results/2026-05-28-plan-2847-claude-subagent.md |

---

## Deliverable

A git-backed cross-machine leadership layer delivered in **two phases**:

- **Phase 1 (safe core, lands first):** committed heartbeat in a git-tracked leader-state file; a **self-fencing execution invariant** — the dispatch loop refuses to `append_lease`/launch unless its *own last successful heartbeat push* is within `STALE_THRESHOLD` (this is what actually prevents the alive-but-cannot-push split-brain, BLOCKER 2); per-secondary watcher that **detects** a stale leader and **alerts** (agents-board + log), no auto-promotion; `term` monotonicity + corruption guard. This alone satisfies the issue's stated minimum ("surface a dead-leader alert within hours").
- **Phase 2 (auto-promotion, behind an opt-in flag):** atomic promotion via git push-race **with post-push confirmation** (winning push is necessary-not-sufficient; re-pull and assert `leader==me && term==mine`; a rejected push ⇒ stand down, **never** `pull --rebase && push`); fencing `term` self-demotes a returning old leader **before each lease append**; redistribution is **flag-only by default for ALL orphaned cards** (the git queue's `dispatch_status` is hardcoded `ready` and is NOT a reliable in-flight signal — BLOCKER 1), with auto re-route gated on a positive freshness proof re-derived from live `gh` issue state at action time, never from the committed queue snapshot.

Both phases are TDD'd with an injectable `LeaderStateStore` for unit tests **plus a real-git integration test** of the push-race CAS (bare repo + two clones), because the most safety-critical property cannot be proven by a mock (BLOCKER-class, per review).

---

## Pseudocode

```
# --- leadership state (git-tracked .claude/dispatch/_leader-state.yaml) ---
LeaderState = { leader: machine, term: int, heartbeat_utc: iso, heartbeat_pid: int }

class LeaderStateStore:                       # injectable for unit tests
    def read() -> LeaderState                 # git pull (best-effort) + parse; raise on corruption
    def claim(new_state) -> ClaimResult       # write file, commit (pathspec) + push;
                                              # PUSHED | REJECTED | PUSH_FAILED(reason)

STALE_THRESHOLD_S  = default 30*60
HEARTBEAT_PERIOD_S = default 10*60
# Coherence invariant (asserted in a test):
#   STALE_THRESHOLD > HEARTBEAT_PERIOD + max_push_latency + max_pull_latency + watcher_cron_period
#   AND STALE_THRESHOLD < lease_TTL (3h)

# --- PHASE 1 leader side: heartbeat + SELF-FENCING (BLOCKER 2) ---
# Wired ONCE per process run AND re-checked at every append_lease call site (L373,L392).
function may_write_leases(store, me, my_term) -> bool:    # gate BEFORE every append_lease
    st = store.read()
    if st.leader != me or st.term > my_term: return False # superseded -> self-demote
    res = store.claim(LeaderState(leader=me, term=my_term, heartbeat_utc=now, pid))
    # CRITICAL: leadership-to-write requires a CONFIRMED PUSH within STALE_THRESHOLD.
    if res != PUSHED: 
        if consecutive_push_failures++ beyond N: self_alert("leader cannot push -> demoting")
        return False                                       # cannot prove reachable -> stand down
    return True
# => every append_lease (L373, L392) becomes: if not may_write_leases(...): raise/demote

# --- PHASE 1 secondary watcher (dispatch-leader-watch.sh -> dispatch_leader.py --check) ---
function check(store, me) -> Status:
    try: st = store.read()
    except Corruption: emit_alert("leader-state corrupt / term regressed"); return UNDETERMINED
    if st.leader == me: return LEADER
    if pull_failed: emit_alert("cannot pull leader-state — undetermined"); return UNDETERMINED  # never promote on inconclusive
    age = now - st.heartbeat_utc
    if age <= STALE_THRESHOLD_S: return OK
    emit_alert(stale leader st, age)                       # Phase 1 stops here
    if AUTO_PROMOTE_ENABLED: try_promote(store, me, st)    # Phase 2 only

# --- PHASE 2 promotion: push-race CAS WITH post-push confirm (MAJOR 4) ---
function try_promote(store, me, st):
    st2 = store.read()                                     # TOCTOU re-read after pull
    if (now - st2.heartbeat_utc) <= STALE_THRESHOLD_S: return  # revived
    res = store.claim(LeaderState(leader=me, term=st2.term+1, heartbeat_utc=now, pid))
    if res == REJECTED: emit_alert("promotion lost to peer"); return  # stand down; NEVER rebase+retry
    # winning push is necessary-not-sufficient: confirm it actually stuck
    st3 = store.read()
    if not (st3.leader == me and st3.term == st2.term+1):
        emit_alert("promotion push landed but state not mine — aborting"); return
    redistribute(dead_leader=st2.leader)

# --- PHASE 2 redistribution: FLAG-ONLY by default; auto only on live-gh proof (BLOCKER 1) ---
function redistribute(dead_leader):
    # queue dispatch_status is hardcoded "ready" — NOT a trustworthy in-flight signal.
    for card in read(.claude/dispatch/<dead_leader>.yaml).cards:
        live = gh_issue_state(card.gh)                     # authoritative, at action time
        if live has active wip/lease-label OR live.state == in-progress:
            flag card "orphaned by dead leader <x>; needs human/gate"   # never auto re-run
        elif live ready AND no wip AND not gated(label+marker semantics):
            re-route via dispatch routing to a healthy machine
        # gated review/merge/plan-approval items: never auto-advanced
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | scripts/ai/dispatch_leader.py | LeaderState + LeaderStateStore (injectable, ClaimResult PUSHED/REJECTED/PUSH_FAILED) + `may_write_leases` self-fence + `check` + `try_promote` + `redistribute` |
| Create | tests/ai/test_dispatch_leader.py | unit TDD (fake store) |
| Create | tests/ai/test_dispatch_leader_gitrace.py | **real-git integration test** of the push-race CAS (bare origin + 2 clones) — proves exactly-one-winner; cannot be mocked |
| Create | scripts/cron/dispatch-leader-watch.sh | per-secondary watcher: pull → check → alert (Phase 1) / promote (Phase 2 flag); logs to logs/ with date stamp |
| Create | .claude/dispatch/_leader-state.yaml | git-tracked seed (leader=ace-linux-1, term=0) |
| Modify | scripts/ai/provider-dispatch-loop.py | emit heartbeat; **gate EVERY append_lease (L373, L392) on `may_write_leases` (confirmed-push self-fence + term)**; self-demote when superseded; route legacy `promotion_token` through the same term/state gate (or retire it) so it can't bypass fencing (MINOR 8) |
| Modify | scripts/monitoring/agents-board.sh | leadership panel: leader, term, heartbeat age, RED if stale; also a leader-side self-alert surface |
| Modify | config/scheduled-tasks/schedule-tasks.yaml | schedule dispatch-leader-watch on secondaries (+ -win variant) with an **explicit cron period** (so the "within one cycle" bound is checkable); declare leader heartbeat cadence |
| Update | docs/plans/README.md | index this plan |

**Heartbeat storage decision (resolve before impl, was an open question):** commit the heartbeat to a **dedicated path** `.claude/dispatch/_leader-state.yaml` only, and squash-amend the heartbeat commit onto a dedicated marker (or accept one rolling commit) to avoid history pollution + auto-sync merge contention. Default: dedicated-ref/amend; confirm in review.

---

## TDD Test List

| Test name | What it verifies | Phase |
|---|---|---|
| test_fresh_heartbeat_no_failover | recent heartbeat → secondary stands down (no claim) | 1 |
| test_leader_with_confirmed_push_may_write_leases | `may_write_leases` true only when claim==PUSHED & term ok | 1 |
| **test_leader_cannot_push_refuses_lease_writes** | claim==PUSH_FAILED/REJECTED → `may_write_leases` False (BLOCKER 2 self-fence) | 1 |
| **test_append_lease_call_sites_gated_on_may_write** | both L373/L392 paths refuse to append when not may_write (no double-leader) | 1 |
| test_leader_consecutive_push_failures_self_alert_demote | N failed pushes → self-alert + demote | 1 |
| test_pull_failure_is_undetermined_never_promotes | pull fails → UNDETERMINED + alert, no promotion | 1 |
| test_term_regression_treated_as_corruption | read() with term < last-seen → raise/alert, no action | 1 |
| test_stale_heartbeat_alert_only_default | stale + auto disabled → alert, no claim | 1 |
| test_threshold_coherence_invariant | STALE_THRESHOLD between (HB+latencies+cron) and lease TTL | 1 |
| test_board_renders_stale_leader_red | agents-board surfaces stale leader | 1 |
| test_stale_heartbeat_triggers_promotion_when_enabled | stale + auto flag on → claim term+1 | 2 |
| test_promotion_lost_race_stands_down_no_rebase | claim==REJECTED → stand down; asserts NO rebase+retry path | 2 |
| **test_promotion_won_then_confirm_pull_mismatch_aborts** | push PUSHED but re-read leader≠me → abort (MAJOR 4) | 2 |
| test_toctou_revived_leader_aborts_promotion | leader revives between read and claim → abort | 2 |
| test_redistribute_flag_only_uses_live_gh_state | redistribution reads live `gh` state, NOT queue dispatch_status (BLOCKER 1) | 2 |
| test_orphan_with_active_wip_flagged_not_rerouted | live wip/in-progress → flag only, never re-run | 2 |
| test_gated_work_never_auto_failed_over | review/merge/plan-approval items untouched | 2 |
| test_returning_old_leader_self_demotes_before_append | superseded old leader self-demotes prior to any lease append | 2 |
| test_legacy_promotion_token_routed_through_term_gate | `--promotion-token` cannot bypass the term/state fence (MINOR 8) | 2 |
| **test_gitrace_exactly_one_winner** (integration, real git) | bare origin + 2 clones both push term+1 → exactly one exit-0, one non-ff; loser stand-down path fires | 2 |
| **test_gitrace_loser_does_not_reland_via_rebase** (integration) | rejected loser must NOT re-land term+1 by rebasing (MAJOR 4) | 2 |

---

## Acceptance Criteria

Phase 1 (required to land):
- [ ] `uv run pytest tests/ai/test_dispatch_leader.py -v` Phase-1 rows pass.
- [ ] No regression: `uv run pytest tests/ai/ -v` (existing 11 dispatch-loop tests green).
- [ ] **Self-fence proven:** a leader whose heartbeat push fails (REJECTED/PUSH_FAILED) refuses every `append_lease` (both L373/L392 sites) — verified by test (closes BLOCKER 2).
- [ ] Simulated dead leader (stale committed heartbeat) is **detected and alerted** within one watcher cycle (cron period pinned in schedule-tasks.yaml).
- [ ] Threshold coherence test passes; term-regression treated as corruption (no action).
- [ ] `bash -n` clean on new/modified shell; watcher logs date-stamped.

Phase 2 (auto-promotion, behind opt-in flag):
- [ ] **Real-git integration test** `test_gitrace_exactly_one_winner` passes (bare origin + 2 clones) — the CAS is proven, not mocked.
- [ ] Loser of the race stands down and does **not** re-land via rebase (`test_gitrace_loser_does_not_reland_via_rebase`).
- [ ] Winning push is confirmed by re-pull (`leader==me && term==mine`) before any redistribution.
- [ ] A returning old leader self-demotes **before** any lease append.
- [ ] Redistribution is **flag-only** unless live `gh` state proves a card is safe to re-route; in-flight/gated work is never auto re-executed.
- [ ] Legacy `--promotion-token` cannot bypass the term/state fence.

Both:
- [ ] Review artifact(s) posted to scripts/review/results/.

---

## Adversarial Review Summary

Plan-stage review by an independent fresh-context subagent (cross-provider Codex/Gemini dispatch unavailable from a Claude-Code session; T3→degraded, documented). Every load-bearing finding was main-session verified against the live code before this revision.

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (subagent, r1) | CHANGES REQUIRED | 3 BLOCKERs + 3 MAJOR + 4 MINOR (below) |

**Verified findings (empirically confirmed by main session):**
- **BLOCKER 1** — `scripts/dispatch/dispatch.py:52` hardcodes `dispatch_status: ready`; all 1489 committed queue cards are `ready`, zero `running`. The original "flag running / reroute ready" safety was dead code → every orphaned card (even in-flight) would be re-routed (double-execution). **Verified** via grep.
- **BLOCKER 2** — the git push-race fences only the *state-file token*, not *execution* (which is gated by a local flock + local `leases.jsonl`). An alive-but-cannot-push leader keeps writing local leases while a secondary promotes → two live leaders, no contention. **Sound** distributed-systems argument.
- **BLOCKER 3** — `run_loop` is a single tick (L342); `append_lease` at L373/L392 has no term re-check; fencing had no insertion point. **Verified** via grep.
- **MAJOR 4** — winning push is necessary-not-sufficient (auto-sync silent-pusher can let a loser re-land via rebase); need post-push confirm + no-rebase-on-reject.
- **MAJOR 5** — cross-machine lease double-count: idempotency key is `issue:provider:machine`, so a new leader's lease on a different machine does not collide; 3h TTL doesn't protect cross-machine.
- **MAJOR 6** — the safety-critical CAS was untested (mock only) → added real-git integration test.
- **MINOR 7** — revive-during-redistribution window → re-derive targets from live `gh` at action time.
- **MINOR 8** — `is_leader_machine` L109 true for any `promotion_token` → unfenced second door. **Verified.**
- **MINOR 9** — term-monotonicity/corruption guard, leader self-alert on push failure, heartbeat storage decision.
- **NIT 10** — pin watcher cron period in the plan.

**Revisions made (this draft):** restructured into Phase 1 (safe alert-only + self-fencing invariant) / Phase 2 (auto-promote behind flag); made the self-confirmed-push the load-bearing execution gate (BLOCKER 2); redistribution is flag-only / live-`gh`-derived, not queue-snapshot (BLOCKER 1); every `append_lease` site gated on `may_write_leases` (BLOCKER 3); post-push confirm + no-rebase-on-reject (MAJOR 4); added real-git integration tests (MAJOR 6); term-corruption guard, promotion_token routed through the fence, cron period pinned, heartbeat-storage decided (MINOR 7-10).

**Overall result:** PASS after revision (Phase-structure + self-fence invariant address the BLOCKERs). A second review pass on the revised plan is warranted before implementation — recommend the user add Codex/Gemini review out-of-session for this T3 distributed-systems design.

---

## Risks and Open Questions

- **Risk — git push latency vs detection window:** if a secondary's `git pull` is stale (network/auth), it may misjudge leader liveness. Mitigation: STALE_THRESHOLD generously above heartbeat period (30 m vs 10 m); watcher treats pull failure as "undetermined", alerts, does NOT promote on inconclusive state.
- **Risk — heartbeat commit noise:** a committed heartbeat every 10 min pollutes git history. Mitigation options (decide in review): (a) amend-and-force the heartbeat commit on a dedicated ref, (b) coarser cadence, (c) a separate lightweight branch. **Open question for user.**
- **Risk — leases are local to the dead box:** redistribution cannot see the dead leader's `leases.jsonl`. The plan deliberately redistributes only from the git-visible queue YAMLs and flags in-flight work rather than guessing. Accept this scope (full lease-state sharing would be a separate change to un-gitignore/publish leases).
- **Risk — double execution:** auto re-routing `running` cards could double-execute work. Mitigation: never auto re-run `running`; flag only. (Hard constraint, tested.)
- **Open:** auto-promote by default, or alert-only with opt-in auto (env/registry flag per machine)? Recommend **alert-only default + opt-in auto** for the first landing (safer), with the auto path fully built+tested behind the flag.
- **Open:** heartbeat cadence (10 min?) and STALE_THRESHOLD (30 min?) — confirm against how long an acceptable throughput halt is.

## Complexity: T3
Cross-machine, systemic, multi-file, introduces a new coordination substrate. Cross-review depth T3 = 3 providers ideally; cross-provider Codex/Gemini dispatch is unavailable from a Claude-Code session, so plan-stage review uses a fresh-context subagent with the fallback documented (T3→degraded), and the user may add Codex/Gemini review out-of-session.
