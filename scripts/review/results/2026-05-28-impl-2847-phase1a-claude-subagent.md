# Code-stage adversarial review — #2847 Phase 1a (dispatch leader failover)

> **Stage:** code/artifact · **Issue:** [#2847](https://github.com/vamseeachanta/workspace-hub/issues/2847) · **Date:** 2026-05-29 · **Complexity:** T3 (Phase 1a slice)
> **Branch:** feat/2847-leader-failover-impl

## Method
Two independent fresh-context subagent rounds (cross-provider dispatch unavailable from a Claude-Code session; degraded T3→1 — a Codex pass out-of-session is recommended before Phase-1b/2). Every load-bearing finding empirically verified by the main session (git plumbing repro).

## Round 1 (initial Phase 1a, git store committed to main) → CHANGES REQUIRED
2 BLOCKERs, both empirically confirmed by main session:
- **BLOCKER 1** — `claim()` committed the heartbeat onto the checked-out `main`; a lost push race left a divergent commit so `git pull --ff-only` failed *permanently* (verified `rc=128 Not possible to fast-forward`). This bricked the leader's own heartbeat AND every secondary's dead-leader read → the one alert the feature exists for goes silent forever. Routine given the 15-min cron + documented auto-sync pusher.
- **BLOCKER 2** — a no-op commit + "Everything up-to-date" push returned PUSHED without a fresh heartbeat landing (invariant held only by timestamp entropy).

## Redesign (dedicated ref + plumbing)
Live state moved to a DEDICATED ref `dispatch-leader-state` (one-file tree). `claim()` builds via `hash-object`/`mktree`/`commit-tree` (no index, no working tree) and pushes with `--force-with-lease=refs/heads/<ref>:<parent>` (server-side atomic CAS against the last-`read()` SHA, TOCTOU-safe). `read()` = `fetch`+`show` (divergence-immune). Verified: `git pull --ff-only` reads the authoritative state even after a divergent local commit.

## Round 2 (re-review of the redesign) → CHANGES REQUIRED, now resolved
Both BLOCKERs confirmed **dead** (architecture correct; CAS confirmed server-side atomic — explicit-value force-with-lease compares against the actual remote ref, not the local remote-tracking ref). Findings + resolution:

| # | Sev | Finding | Resolution |
|---|-----|---------|------------|
| 1 | MEDIUM | `claim()` could leak `StoreUnavailable` (contract is `ClaimResult`) when fetching without a prior read on a network failure | wrapped → returns `PUSH_FAILED`; test `test_gitstore_claim_network_failure_returns_push_failed` |
| 2 | MEDIUM | missing-ref vs failure rested on locale-fragile English error-string matching; comment falsely said git exits 0 on missing ref (it exits 128) | structural `git ls-remote --exit-code` (rc 2 = absent); comment fixed; test `test_gitstore_fetch_failure_is_unavailable_not_bootstrap` |
| 3 | LOW | `commit-tree` w/o committer identity → `PUSH_FAILED` (fails safe, mislabeled) | left (fails safe; noted) |
| 4 | LOW | heartbeat wrote caller's `my_term` not committed `st.term` (latent term-bump foot-gun) | heartbeat now uses `st.term` |
| 5 | LOW | race tests sequential not concurrent | adequate for the CAS property (Phase 1); note for Phase-2 threaded contention test |
| 6 | LOW | no tests for fetch-failure / identity classification | added the two classification tests (#1/#2) |

## Verification
TDD RED→GREEN. **30 passed** (19 dispatch_leader incl. no-main-mutation, push-race exactly-one-winner, BLOCKER-1 no-brick regression, network-failure classification; + 11 existing dispatch-loop, no regression). CLI degrades to UNDETERMINED (rc 0) on an uninitialized ref — no crash, no false alert.

## Scope note
`may_write_leases` (the self-fence primitive) is provided + unit-proven but NOT yet wired into `provider-dispatch-loop.py:append_lease` — that is **Phase 1b**. agents-board panel + auto-promotion are Phase 1b/2. This slice ships the primitive + the detect/alert watcher.

## Verdict
**APPROVE** after the redesign + MEDIUM fixes. Both original BLOCKERs are architecturally eliminated and regression-tested. Recommend a Codex cross-review out-of-session before Phase-1b wires the gate into the live lease path.
