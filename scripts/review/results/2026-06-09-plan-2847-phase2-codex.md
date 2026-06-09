# Codex adversarial review — #2847 Phase 2 auto-promotion plan

Date: 2026-06-09
Plan: `docs/plans/2026-05-29-issue-2847-phase2-auto-promotion.md`
Baseline checked: `origin/main` fetched 2026-06-09

## Verdict

CHANGES REQUIRED. Do not implement Phase 2 auto-promotion from the current plan.

## Findings

### BLOCKER: Phase 2 approval state is not clean

The merged approval marker on `origin/main` says the approved scope was Phase 1 first:

`Issue #2847 plan approved ... Scope note: implementing Phase 1 (alert-only + self-fence) first per the plan.`

The Phase 2 plan branch is still plan-review and was never merged to `main`. The issue has `status:plan-approved`, but this detailed highest-stakes Phase 2 plan still needs an explicit approval record before implementation.

### BLOCKER: Cluster-wide fence readiness is asserted, not enforceable

The plan correctly says auto-promotion is unsafe unless `DISPATCH_ENFORCE_LEADER_FENCE=1` is enabled on every dispatch-capable machine. Current code still defaults the fence off in `scripts/ai/provider-dispatch-loop.py`, and current tests only cover local env parsing and fake-store behavior.

Before any auto-promotion path exists, the plan needs an enforceable readiness gate that enumerates the live dispatch-capable machines and fails closed if any machine is not fence-enabled, not reporting current leader-state, or not running the watcher. A local `try_promote(... fence_enabled=True)` unit test is insufficient.

### MAJOR: Per-tick fencing contradicts the no-double-dispatch claim

`may_write_leases` documents that it should be called immediately before every lease append, but `provider-dispatch-loop.py` currently checks the fence once per `run_loop` tick and then appends one or more leases.

The Phase 2 plan accepts a duplicate window up to `max_implementation_per_run`, while acceptance also claims no cross-machine double-dispatch. That is not a no-split-brain proof. The repaired plan should either:

- move the fence check to each lease append path before enabling auto-promotion, or
- weaken acceptance language and explicitly accept bounded duplicates as an operational tradeoff.

For this system, the safer path is per-append fencing before auto-promotion.

### MAJOR: Machine-independent idempotency is specified but not wired to the live contract

The plan pseudocode reroutes with an `issue:provider` idempotency key, but current live code defines and writes `issue:provider:machine`. The file-change list does not explicitly change `lease_idempotency_key`, `active_lease_for`, `make_lease`, and tests that assert the existing machine-scoped key.

A mock redistribution test could pass while the real dispatch loop still double-issues across machines. The repaired plan needs a concrete migration of the idempotency contract, or a separate cross-machine guard such as a GitHub WIP marker acquired before lease creation.

### MAJOR: Redistribution targets full machine backlog

`scripts/dispatch/dispatch.py` writes each machine's full backlog and hardcodes `dispatch_status: ready`; `wip_eligible` is the only queue-file hint that a card is currently claimable. The Phase 2 plan loops every card in the dead leader queue and checks only live open/unclaimed/not-gated status.

The repaired plan must restrict redistribution to work that is both live-eligible and route-eligible at action time: open issue, approval marker, status label, not gated/review/merge-only, machine/provider route still valid, and `wip_eligible` or equivalent recomputed from the current routing source.

### MAJOR: Watcher/CLI behavior lacks shell-level coverage

The plan changes `scripts/cron/dispatch-leader-watch.sh`, but the test list is centered on Python unit/integration tests. The watcher is where env flags combine:

- auto-promote off/on
- fence off/on
- stale/fresh/undetermined leader
- exit code behavior

The repaired plan needs shell/CLI tests for the watcher matrix, not only `try_promote` unit tests.

### MAJOR: Legal/security gate is missing from acceptance

The repo hard gate requires `scripts/legal/legal-sanity-scan.sh`. The Phase 2 plan acceptance omits it. Add the legal scan or a scoped/legal documented fallback if the repo-wide scan is blocked by unrelated legacy matches.

### INVALIDATED REVIEW CLAIM: newer `scripts/operations/*lease*.py` files

A subagent review claimed `scripts/operations/dispatch_lease.py` and `scripts/operations/git_ref_lease.py` exist on current `origin/main`. Local verification against fetched `origin/main` found those paths do not exist. Do not base replanning on that claim unless a future branch intentionally introduces those files.

## Recommendation

Convert Phase 2 into a repaired plan with two explicit gates:

1. Phase 2a: fence readiness + per-append fence + watcher shell coverage, with auto-promotion still impossible.
2. Phase 2b: auto-promotion and redistribution behind `DISPATCH_ENABLE_AUTO_PROMOTE`, after Phase 2a is merged and explicitly approved.

Implementation should not start until the repaired plan is reviewed and approved.
