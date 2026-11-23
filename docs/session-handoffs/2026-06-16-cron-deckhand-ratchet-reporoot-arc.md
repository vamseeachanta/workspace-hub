# Session handoff — cron→deckhand→ratchet→REPO_ROOT arc

> Date: 2026-06-16 (into 2026-06-17 UTC) · Machine: ace-linux-1 · Runner: Claude
> Memory: `project_cron_recovery_and_deckhand_protections_down_2026_06_14` (auto-memory) carries full detail.

## TL;DR

All substantive work is **delivered and merged to `origin/main`**. One administrative step is outstanding: the owner-gated close of workspace-hub#3179 (the `!`-prefix verify+close command would not execute this session — see Blocker).

## What shipped (all merged, verified on origin/main)

| Item | PR / commit | State |
|---|---|---|
| Cron fleet sweep (ace-linux-1) | n/a (live crontab + working-tree fixes) | done |
| deckhand attachment-gate restore + fail-loud alert | deckhand#356/#358, gateway restarted | closed |
| Pre-push tier-1 repo resolver (sibling layout) | #3127 / #3136 | closed |
| ruff baseline/ratchet | #3146 / PR #3161 | closed |
| mypy baseline/ratchet + exit-code discipline | #3148 / PRs #3174 + au#93 | closed |
| Worktree-ownership guard | #3143 / #3153 | merged |
| digitalmodel: repair/retire 12 corrupted `.py` files | digitalmodel#788 / PR #790 | merged |
| Un-exempt digitalmodel in mypy-baseline | #3178 / PR #3178 (`e5bb77806`) | merged + closed |
| **REPO_ROOT-under-hook fix (run-all-tests + run-benchmarks)** | **#3179 / PR #3183 (`a90c594e6`)** | **merged; issue close pending** |

Net: the `check-all` pre-push gate is now fully ratcheted (ruff + mypy) on all 4 tier-1 repos, and the worktree pre-push `run-all-tests` false-FAIL is fixed at the source.

## #3179 — the only open thread (administrative)

- **Code:** merged, live on `origin/main`. `scripts/testing/run-all-tests.sh:20` and `run-benchmarks.sh` now use the git-free structural root `REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"` (matches `check-all.sh:8`; immune to the `GIT_DIR`-without-`GIT_WORK_TREE` hook skew). Test: `tests/quality/test_run_all_tests_repo_root.sh` (regression A/B + contract C/D).
- **Review:** plan T3 (Claude+Codex+Gemini; design pivoted to git-free per r2), code review APPROVE, legal PASS.
- **Completeness gate:** record stamped on the issue body (evidence class, **100% ≥ 80**, valid). Gate config verified: `COMPLETENESS_OWNERS=vamseeachanta`, `SEPARATE_CLOSER` unset (solo close allowed), label `status:completeness-verified` exists.
- **BLOCKER:** the `! gh issue edit … --add-label status:completeness-verified` / `! gh issue close …` commands produced **no stdout and no GitHub timeline event** across 4 attempts — the `!` invocation is not firing for these specific lines (earlier `git push` / `gh pr merge` via `!` DID work). Not a gate problem.
- **TO CLOSE (owner action, either route):**
  - Web UI on issue #3179: add label `status:completeness-verified`, then Close. **(recommended — bypasses the broken `!`)**
  - Or plain terminal (not `!`): `gh issue edit 3179 --repo vamseeachanta/workspace-hub --add-label status:completeness-verified && gh issue close 3179 --repo vamseeachanta/workspace-hub`
  - Anti-forgery: do NOT edit the issue body after applying the label (the label must post-date the stamped record — currently satisfied).

## Repo / working-tree state at exit

- **workspace-hub:** on local branch `plan/3179-reporoot-hook-resolution` (merged via squash `a90c594e6` → now stale; safe to `git branch -D`). Local main is ~4 behind origin/main (auto-sync drift; `git pull --ff-only` to refresh).
- **Stale local branches (merged, safe to delete):** `plan/3179-reporoot-hook-resolution`, `feat/3148-unexempt-digitalmodel`. Remote copies deleted at merge.
- **digitalmodel:** branch `fix/788-corrupted-py-files` merged via PR #790; on `main`.
- **Worktrees:** none (the session worktree `wh-unexempt-wt` was nuked by the #3153-gap cleanup mid-session; pruned). Commits survived in shared refs.
- **Stashes:** none.
- **Uncommitted:** only generated/cron churn (provider dashboards, session-signals, `.claude/memory/topics/` mirrors) — NOT this session's; plus `scripts/testing/coverage-reports/WRK-1067-coverage-*.txt` (byproduct of the `--coverage` regression test, gitignored class). Nothing of mine left uncommitted.
- **No external comms sent.** Memory updated.

## Deferred / backlog (not started)

1. **#3179 follow-on:** ~32 other `git -C … rev-parse --show-toplevel` call sites share the hook-skew class (incl. same-dir off-pre-push-path `run-cross-repo-integration.sh`, `refresh-fixtures.sh`). Convert via a shared git-free helper or the structural pattern; r2 captured the design notes (native subshell `(unset GIT_DIR GIT_WORK_TREE; git …)`, no `|| true` swallow) in the #3179 plan Design §3. File as a tracked issue when picked up.
2. **#3153 worktree-guard GAP:** worktrees under `/mnt/local-analysis` are still nuked mid-session despite the merge — lost `wh-unexempt-wt` this session. Needs its own diagnosis.

## Gotchas captured this session (for the next runner)

- `completeness_score.py` import dies if the helper script runs from `/tmp` (a stray `/tmp/inspect.py` shadows stdlib) → use `PYTHONSAFEPATH=1`. The gate runner needs `REPO=vamseeachanta/workspace-hub` env or it builds `repos//issues`.
- This repo's `origin/main` moves fast (parallel agents) → always verify a branch with the **3-dot** diff (`origin/main...branch`), and check `git diff --stat origin/main..HEAD` size before any merge (stale-branch trap).
- Pushes from this machine still need `GIT_PRE_PUSH_SKIP` (human-only) until the config-drift `repo_missing` sibling-absence warning is also addressed; the #3179 fix removes the *run-all-tests* contribution to that friction.
