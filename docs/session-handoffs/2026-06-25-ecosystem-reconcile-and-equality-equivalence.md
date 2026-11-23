# Session handoff — 2026-06-25 · Ecosystem reconcile + machine-equality equivalence

## Scope

Built and shipped a cross-machine **reconcile** capability, executed a large stale-branch/
worktree cleanup, and added **equivalence guidance** to the live machine-equality matrix.
All work landed on `main` via PR; one large prune was executed locally on `ace-linux-2`.

## Shipped (all PRs MERGED)

| PR | What |
|---|---|
| [#3234](https://github.com/vamseeachanta/workspace-hub/pull/3234) | Collapsible equality matrix (4 row-groups, default collapsed, per-machine worst-of rollups) + role/work-policy notes; `reconcile-ecosystem.sh` + `ecosystem-equivalence-reconcile` skill; removed orphan `equality-licensed-win-2.yaml` |
| [#3235](https://github.com/vamseeachanta/workspace-hub/pull/3235) | Squash-merge-aware branch detection (`gh pr list --state merged`, guard-gated `-D`); equality refresh delegates to canonical `equality-matrix-cron.sh`; `build-equality-matrix.py --json [--machine]` |
| [#3236](https://github.com/vamseeachanta/workspace-hub/pull/3236) | Fix: `worktree_guard.py` invoked with target-repo cwd (was checking workspace-hub's worktrees for sibling branches) |
| [#3238](https://github.com/vamseeachanta/workspace-hub/pull/3238) | "Achieving equivalence" section on the live matrix — per-machine actions generated from live verdicts + embedded reconcile prompt + by-design callouts |

Live link (updates on Pages deploy):
https://vamseeachanta.github.io/workspace-hub/machine-equality-matrix.html

## Executed cleanup (local, `ace-linux-2`, no remotes touched)

- **~186 squash-merged local branches deleted** across 11 repos (deckhand 63→10, digitalmodel 45→3, workspace-hub 38→8, worldenergydata 30→5, llm-wiki 20→1, …) — guard-gated, PR-merge-confirmed.
- **385 stale remote-tracking refs pruned** (`git remote prune origin`) + worktree admin pruned.
- **2 stale deckhand worktrees removed** (`cathodic-templates`, `parametric-bot-wiring` — PR-merged + clean) and their branches.
- **`digitalmodel` fast-forwarded** (was behind 3, clean).

## New operator surface (one keystroke, all machines)

- Claude Code / Gemini CLI: `/reconcile-ecosystem` (+ `--apply`, `--apply --stash-dirty`, `--apply --equality`)
- Any shell / Codex / Hermes: `bash scripts/readiness/reconcile-ecosystem.sh [--apply …]`
- Report-first; guard-gated; never discards dirty; ff-only; `dev-primary` destructive-locked. Each box reconciles its own column.
- Equality chain is single-sourced: leaves `collect-equality.{sh,ps1}` + `build-equality-matrix.py` → `equality-matrix-cron.sh` (Linux) / `windows/equality-report.ps1` (Windows) → `refresh-equality-matrix.{sh,ps1}` (operator publish).

## Repo state at exit

- **workspace-hub `main`**: clean, synced to origin (canonical). Handoff lands via this branch's PR.
- Earlier a shared-clone HEAD-switch left local `main` diverged with the #3237 flowchart commit; that commit is safe on `origin/docs/issue-lifecycle-flowchart-page`, and the auto-sync cron realigned local `main` — **no action needed**.
- **Preserved, NOT touched** (active work / judgment calls): dirty trees in aceengineer-strategy, llm-wiki*, deckhand, deckhand-sandbox, achantas-data, etc. (live uncommitted work per memory); recent WIP stashes (digitalmodel 2, assethold/assetutilities/deckhand 1); unmerged code (deckhand-sandbox 6 unpushed, sabithaandkrishnaestates 1); behind+dirty repos (deckhand stuck `b0799cf` behind 20, llm-wiki behind 166); the genuinely-unmerged `feature/206` deckhand worktree + `.deckhand-guard`/`.deckhand-sweep` automation worktrees.

## No external actions taken

No emails/messages sent, no client-facing artifacts published, no remote branches force-pushed or deleted, no merges to protected mains outside the four PRs above (all user-approved). Cleanup was local-branch/ref/worktree only.

## Current equivalence status + fastest path to green

| Machine | Gaps | Note |
|---|---|---|
| ace-win-1 | 22 (all MISSING-EVIDENCE) | **not reporting** — run the collector once → clears all |
| ace-win-2 | 11 | 15-day-stale report → ~10 stale divergences; solvers BELOW-BASELINE is by-design (licence probe) |
| dev-primary | 14 | 9 provider rows by-design (Hermes host, no Claude); 5 uniform diverge vs stale peer |
| dev-secondary | 5 | uniform divergence driven by the stale ace-win-2 peer |
| home-win / macbook-portable | clean | UNREACHABLE (deferred) |

**Fastest path:** ① collector on **ace-win-1** → ② `-RefreshMatrix` on **ace-win-2** → ③ re-collect both Linux boxes on fresh `main` → re-judge; residual divergence is then *real* config drift (skills→symlink repair, harness→soul-runtime, scheduler→cron). The page's "Achieving equivalence" cards spell this out per box.

## Next steps (operator)

1. Run `/reconcile-ecosystem --apply` on the **other** machines (ace-linux-1, Windows boxes) to self-clean their stale branches/refs.
2. Bring **ace-win-1** into reporting (first equality collect) and **ace-win-2** up to date (`-RefreshMatrix`).
3. Optional: push/PR the unmerged code (deckhand-sandbox 6, sabithaandkrishnaestates 1) and resolve the deckhand `b0799cf` stuck clone (shared-clone hazard) when convenient.
