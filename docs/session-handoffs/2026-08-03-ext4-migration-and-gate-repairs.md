# Session handoff — 2026-08-03: ext4 migration, enforcement-gate repairs, dynacard defects

## ⚠ The working surface changed

**`/mnt/ace/ws` is now the canonical workspace root on `ace-linux-1`.**

`/mnt/local-analysis` remains as a **compatibility symlink** → `/mnt/ace/ws`, so every existing path, hook, cron entry and config keeps working unchanged. New work should reference `/mnt/ace/ws` directly.

| | |
|---|---|
| Root | `/mnt/ace/ws` (ext4, `/dev/sda1`, 2.1 TB free) |
| Legacy path | `/mnt/local-analysis` → symlink, still valid |
| Old volume | `/dev/sdc1` NTFS-FUSE — **detached but intact**; fstab line 12 commented; backup at `/etc/fstab.bak-premigration` |

**Measured effect** (real repos, warm index):

| repo | `git status` before | after |
|---|---:|---:|
| workspace-hub | 11,576 ms | **23 ms** (503×) |
| digitalmodel | 3,577 ms | **15 ms** (238×) |
| worldenergydata | — | **9 ms** |

`git describe --dirty`: 4,763 → 217 ms (workspace-hub); 8,899 → 799 ms (digitalmodel). `uv sync --frozen` now 2–19 s per repo.

Full detail and both migration traps: **#3793** (closed).

## Repo states at exit

| repo | branch | HEAD | dirty |
|---|---|---|---|
| workspace-hub | `main` | `06f56acfb` | 12 (bridge-managed memory + generated) |
| digitalmodel | `fix/3787-startup-tax` | `4a39e184` | 0 |
| worldenergydata | `fix/3787-startup-tax` | `ce3a6f26` | 0 |
| assetutilities | `feat/wf-api-3282-3295-resultenvelope` | `c30a02c` | **57 — pre-existing, not this session** |
| assethold | `main` | `4cf59a1` | 0 |

No agents, watchers, or rsync running. No external actions taken (no emails, no outward posts).

## Merged this session

**workspace-hub (post-handoff)** — `944173d4d` restores the auto-sync-reverted installer and pins `REVIEW_GATE_STRICT`; closes #3796.

**digitalmodel** — #1953 (tagging classifier abstains), #1954 (fillage computed, mode count derived), #1956 (field-health stops routing to the Gibbs solver), #1957 (uv caching 9/9)

**workspace-hub** — #3779 (machine inventory), #3782 (pre-push restored to version control + merge-base scoping), #3783 (installer extension point, dead gates re-wired, review gate made blocking), #3785 (uv caching 11/11 + `--frozen`)

## Open, with plans committed

| Issue | State |
|---|---|
| **#3787** | Startup tax. Plan **approved**; WIP commit `f4520e26` on `fix/3787-startup-tax` in worldenergydata — **unverified**, with an open question: it drops `config.pluginmanager.register(...)`, which may disable the regression analysis rather than defer it. Do not open a PR from that state |
| **#3790** | 487 excluded test files. Plan committed, needs review. **Precondition** for the CI-tiering work |
| CI tiering | `docs/plans/2026-08-03-ci-tiering-and-domain-routing.md`, plan-review, T3 |
| **#3781** | Three dead gates re-wired; stage-prompt drift left to CI (measured 206 s — too slow for a push gate) |
| dm#1958 | `workflow-automation-tests.yml` fails on main — `pytest-cov` missing, undetected ~2 months because the workflow never ran |
| dm#1857 | Gibbs solver returns an affine rescale. **Deferred by owner decision** — `everitt_jennings` already reproduces reference cards at 0.9% nRMSE vs 17.3% |

## ⚠ #3796 — auto-sync reverted merged work (FIXED, but read this)

**Closed.** The root cause is the most consequential finding of the session and changes how to work in this repo.

`382e4a180 chore(gtm): weekly job market scan refresh 2026-08-03` deleted **106 lines** from `scripts/enforcement/install-hooks.sh`, removing the entire #3781 change that had merged hours earlier in `9cfe69501` (#3783) — the extension-point sentinel, the refuse-without-sentinel guard, the reachability-aware idempotence, and `strip_dead_tail()`. The same commit also deleted three plan files and a plan-approval marker (`0+/137-`, `0+/101-`, `0+/89-`, `0+/41-`).

**Mechanism:** the PR merged **on GitHub** while the local working tree still held the pre-merge copy of the file. Auto-sync committed the dirty tree, writing stale content back over the merged version — under a commit message about a job market scan.

**Why this is worse than the sweep contamination already on record:** that variant *adds* unrelated files to a commit, which is visible in any PR diff. This one *deletes merged code under an unrelated message*, which is invisible. It surfaced only because `test_refuses_without_sentinel` existed and went red — a test written for the safety property caught that property being removed.

**Operational rule that follows:**
- **After any PR merges, `git pull` before doing anything else in that repo.** Merged-on-GitHub plus a stale local tree is a pending revert waiting for the next auto-sync tick.
- When a merged feature "isn't there", do **not** assume the merge failed. Run `git log --oneline -3 -- <file>` and look for a later unrelated commit; `git show --numstat <sha> | awk '$2>$1'` lists what a commit net-deleted.
- Restore verbatim: `git show <merge-sha>:<path> > <path>`.

**Second defect, same issue:** the pre-push suite passed in CI and failed on a developer machine. `_run_hook` set `DISABLE_ENFORCEMENT`, but `require-review-on-push.sh` does not honour it (only `require-stage-prompt-drift.sh` does, `:28`), so the review gate stayed live — and since #3781 sources `enforcement-env`, it blocks locally and is advisory in CI. Now pinned in the harness by **unconditional assignment**; the first attempt used `env.setdefault(...)` and changed nothing, because `setdefault` defers to the ambient value that was the problem.

**Verified:** 79 passed, 1 skipped, **with no environment pin on the pytest invocation** — that is the acceptance criterion. Both changes confirmed on `origin/main`. Commit `944173d4d`.

## Follow-ups from the migration

1. **Fleet divergence** — `ace-linux-2` still mounts real NTFS at `/mnt/local-analysis` (fstab line 15 sshfs-mounts it here). Equality/readiness tooling will see the machines differ structurally. Replicate there, or record as intentional.
2. **Do not repurpose `/dev/sdc1`** until the new layout has run for a while — it is the rollback.
3. **43% of what migrated gains nothing from ext4** — `agent-worktrees` (27 GB, mostly merged branches) and `phone-media` (28 GB archived media). A worktree sweep would reclaim most of 27 GB.

## Cleanup audit

- **CLEAN** — no agents running; no session-created residue in repos; both trees self-consistent; all merged branches deleted locally and remotely.
- **EXPECTED** — 12 dirty files in workspace-hub (bridge-managed `.claude/memory/*` and generated artifacts); `/mnt/local-analysis` symlink retained by design; NTFS volume retained as rollback.
- **UNEXPECTED** — 57 dirty tracked files in `assetutilities` on a feature branch. **Pre-existing**, observed by a read-only audit agent before this session's work; not touched here. Worth triaging.
