# Plan for #2826: Reconciler Phase 2 — activation (cron + GitHub App + nudge)

> **Status:** draft (needs adversarial review → user approval) · **Complexity:** T2 · **Date:** 2026-05-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2826 · **Parent:** #2802 (Phase 1 engine merged: #2820+#2823) · #2795 · **Client:** N/A

## Resource Intelligence Summary
- **Engine (done):** `scripts/kanban/reconcile.py` + `.github/workflows/kanban-reconcile.yml` on `main` (merged #2820/#2823); 13 tests; cron is **commented** with a `# TODO(#2802 phase 2)` block; `workflow_dispatch` live; `permissions: contents:write, issues:read`.
- **Gap:** the Action authenticates `gh` with the default `GITHUB_TOKEN`, scoped to workspace-hub only → cannot read sibling-repo issues. The workflow-contract test currently asserts cron stays **deferred** (must flip when activated).
- **Standards/Wiki:** N/A.

## Problem
The reconciler engine is built+tested but does not run automatically, so issues do not yet auto-appear. Activation needs (a) a cross-repo issue-read token and (b) the cron enabled, without re-introducing the P1s the plan-stage review caught (concurrency cancel, push race, self-loop).

## Approach
1. **GitHub App (human install step):** create a fine-grained App — `issues:read` on the active sibling repos, `contents:write` on workspace-hub. Store the App id + private key in **one org-level secret**. The workflow mints an installation token at run time and exports it for `gh issue list` (cross-repo reads), while the **contents push keeps the default `GITHUB_TOKEN`** so it does not retrigger CI (anti-loop).
2. **Enable cron:** uncomment the `*/20` schedule. Concurrency group `kanban-reconcile` with `cancel-in-progress: false` is already correct (no card-dropping). Bounded push-retry already classifies non-fast-forward (from #2823).
3. **Optional `repository_dispatch` nudge (low-latency):** per-repo lightweight workflow on `issues.opened/reopened/transferred` → `repository_dispatch` to trigger an early reconciler run; **excludes `labeled`** (high-frequency); workspace-hub ignores self-generated dispatches. Correctness never depends on it.

## Scope
In: App install runbook + secret wiring; token step in the workflow; uncomment cron; flip the workflow-contract test to assert cron **active**; per-repo nudge workflow (templated). Out: Phase 3 Hermes loader (#2827); GraphQL fetch (#2828).

## Risks & mitigations
| Risk | Mitigation |
|---|---|
| App token leaks / over-scope | fine-grained `issues:read` only on siblings; org secret; never echoed in logs |
| Scheduled run reads a partial cross-repo set | #2823 count-delta fail-closed guard already aborts on shrink |
| Cron + human + autosync push contention | bounded non-fast-forward retry (#2823) |
| Nudge storm / loops | exclude `labeled`; ignore self-dispatch; cron is the guarantee |

## Acceptance criteria
1. App installed; one org secret; workflow mints an installation token and `gh issue list` reads all active sibling repos (verified on a **2-repo pilot run** first — the original Phase-1 pilot AC).
2. Cron enabled; a scheduled run reconciles end-to-end and commits one batched commit with the default token (no CI retrigger).
3. Workflow-contract test updated to assert cron **active** + token step present; tests green.
4. Nudge workflow fires a reconciler run on `issues.opened` and excludes `labeled`.

## Dependencies / sequencing
Do **#2828** (GraphQL fetch hardening) before or with this, so the *scheduled* reconciler is robust against partial fetches. Human App-install is the gating manual step.
