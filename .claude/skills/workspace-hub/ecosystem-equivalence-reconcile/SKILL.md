---
name: ecosystem-equivalence-reconcile
description: Bring THE CURRENT computer back to ecosystem + machine-equality equivalence — clean repo-hygiene drift (dirty trees, stale branches/worktrees/stashes) and remediate every non-OK equality-matrix verdict. Report-first; destructive actions are guard-gated and opt-in.
type: workflow
version: 1.0.0
category: workspace-hub
last_updated: 2026-06-24
source: internal
tags: [equality, hygiene, reconcile, corrective-action, worktree, branches, multi-machine]
related_skills: [repo-ecosystem-hygiene, worktree-branch-sync-hygiene, repo-sync, machine-equality-matrix-live-link]
freedom: low
---

# Ecosystem + Equality Reconcile

Run this **on any computer** to drive it back into equivalence with the rest of the
ecosystem. It reconciles two surfaces at once:

1. **Repo-ecosystem hygiene** — dirty working trees, behind/ahead upstream, merged-but-
   undeleted branches, stale worktrees, stale stashes, across this machine's sibling repos.
2. **Machine-equality** — every cell in this machine's column of the
   equality matrix (`docs/reports/machine-equality-matrix.html`) that is not
   `OK / CONFORMS / EQUAL / PARITY`.

Driver: `scripts/readiness/reconcile-ecosystem.sh` (repo-root relative).
It is **report-first** — the default run mutates nothing.

## Safety boundary (load-bearing)

The driver inherits the deny-by-default guard (`scripts/lib/worktree_guard.py`, #3143). It
**never**:
- discards dirty work (it stashes — recoverable — only with `--apply --stash-dirty`),
- deletes a branch that is unmerged, current, or checked out in any live worktree,
- removes a worktree it cannot prove it owns (foreign / active-session worktrees are surfaced, not pruned),
- does anything but **fast-forward** on remotes (no reset/force/rebase).

Every action is classified before anything runs:

| Class | Meaning | `--apply` behaviour |
|---|---|---|
| `AUTO-SAFE` | reversible / guard-approved | executed |
| `NEEDS-APPROVAL` | destructive or judgement-dependent | printed only — you run it after review |
| `OPERATOR-ONLY` | off-box (Windows licence probe, hardware, remote host) | printed only |

## Procedure

```bash
# 1. SEE the plan (read-only — safe anywhere, anytime)
bash scripts/readiness/reconcile-ecosystem.sh
bash scripts/readiness/reconcile-ecosystem.sh --json   # machine-readable, for CI/dispatch

# 2. APPLY only the auto-safe subset (ff-pulls clean repos, etc.)
bash scripts/readiness/reconcile-ecosystem.sh --apply

# 3. Resolve dirty trees deliberately (recoverable stash), then re-pull
bash scripts/readiness/reconcile-ecosystem.sh --apply --stash-dirty

# 4. After the tree is clean + fetched, refresh THIS machine's equality report + matrix
bash scripts/readiness/reconcile-ecosystem.sh --apply --equality
```

Work the `NEEDS-APPROVAL` list by hand — each line prints the exact command. For branch /
worktree disposal at scale on the primary, prefer the existing guarded cron
(`scripts/cron/daily-cleanup.sh --dry-run` then live) rather than ad-hoc deletion.

## Machine policy (who may do destructive cleanup)

| Machine (role) | Hygiene cleanup | Notes |
|---|---|---|
| `dev-primary` (ace-linux-1, control-plane) | **report-only for branch/worktree** | runs the intentional worktree-per-feature automation + owns the `daily-cleanup` cron; the driver auto-sets `DESTRUCTIVE_OK=0` here so it never trampls live worktrees |
| `dev-secondary` (ace-linux-2) | full auto-safe eligible | scratch/execution box |
| `ace-win-1`, `ace-win-2` (Windows) | scout-only; bug-fixes OK | licensed hosts; do max work on Linux, keep these thin |

## Equality verdict → corrective action (the playbook)

The driver maps each non-OK verdict in this machine's column to a fix:

| Verdict | Cause | Corrective action |
|---|---|---|
| `STALE-CHECKOUT` | dirty / behind / ahead / origin-ref > 12h | clean the tree (commit-push or `--stash-dirty`), `git fetch origin main`, re-run `collect-equality.sh` |
| `MISSING-EVIDENCE` (machine dim) | no fresh report on this box | run `collect-equality.sh` here |
| `MISSING-EVIDENCE` (`harness:<provider>:*`) | provider/ capability absent — or no Claude baseline on this host (Hermes-only box grades these by design) | install/auth the provider; on a Hermes-only host, expected |
| `BELOW-BASELINE` `solvers` | licence probe emits `present` ≠ `licensed` | **operator/Windows** licence-probe follow-up (PR #2850 note) |
| `BELOW-BASELINE` `data_access` | a required tier-1 sibling isn't cloned | clone the missing repo under the sibling root |
| `BELOW-BASELINE` `compute` | under cores/ram/gpu floor | **operator** — hardware, or reconcile `harness-config.yaml` `compute_floor` |
| `DIVERGES` / `NO-MAJORITY` `skills` | tracked symlink materialized as a text file (`core.symlinks=false`) | `git config core.symlinks true`; `rm` + `git checkout --` the symlink paths |
| `DIVERGES` / `NO-MAJORITY` `harness` / `behavior` | runtime/config drift | `build-soul-runtime.sh` + `install-soul-runtime.sh`, then re-collect |
| `DIVERGES` / `NO-MAJORITY` `scheduler` | cron drift | `setup-cron.sh --check`, then re-collect |
| `DIVERGES` / `NO-MAJORITY` (other) | often a **stale peer** report inflating divergence | re-collect on this box first; if it persists, reconcile the config |
| `UNREACHABLE` / `EXPECTED-DIFF` / `EXPECTED-DIVERGENCE` | by design | no action |

## After reconciling

Re-render and (if pushing) refresh the live link per
[[machine-equality-matrix-live-link]]. A divergence that survives a clean re-collect is a
**real** config drift, not a stale-report artifact — fix the config, don't just re-collect.

## Related

- `repo-ecosystem-hygiene` — the read-only detector this complements (it reports; this remediates).
- `worktree-branch-sync-hygiene` — branch/worktree disposal workflow for the NEEDS-APPROVAL items.
- `scripts/cron/daily-cleanup.sh` — the guarded primary-host cron that owns at-scale auto-disposal.
