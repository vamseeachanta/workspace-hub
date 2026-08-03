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

**digitalmodel** — #1953 (tagging classifier abstains), #1954 (fillage computed, mode count derived), #1956 (field-health stops routing to the Gibbs solver), #1957 (uv caching 9/9)

**workspace-hub** — #3779 (machine inventory), #3782 (pre-push restored to version control + merge-base scoping), #3783 (installer extension point, dead gates re-wired, review gate made blocking), #3785 (uv caching 11/11 + `--frozen`)

## Open, with plans committed

| Issue | State |
|---|---|
| **#3796** | `install-hooks` refusal test fails on main; pre-push suite passes only with `REVIEW_GATE_STRICT=0`. **Highest priority** — the refusal is the safety property of #3781 |
| **#3787** | Startup tax. Plan **approved**; WIP commit `f4520e26` on `fix/3787-startup-tax` in worldenergydata — **unverified**, with an open question: it drops `config.pluginmanager.register(...)`, which may disable the regression analysis rather than defer it. Do not open a PR from that state |
| **#3790** | 487 excluded test files. Plan committed, needs review. **Precondition** for the CI-tiering work |
| CI tiering | `docs/plans/2026-08-03-ci-tiering-and-domain-routing.md`, plan-review, T3 |
| **#3781** | Three dead gates re-wired; stage-prompt drift left to CI (measured 206 s — too slow for a push gate) |
| dm#1958 | `workflow-automation-tests.yml` fails on main — `pytest-cov` missing, undetected ~2 months because the workflow never ran |
| dm#1857 | Gibbs solver returns an affine rescale. **Deferred by owner decision** — `everitt_jennings` already reproduces reference cards at 0.9% nRMSE vs 17.3% |

## Follow-ups from the migration

1. **Fleet divergence** — `ace-linux-2` still mounts real NTFS at `/mnt/local-analysis` (fstab line 15 sshfs-mounts it here). Equality/readiness tooling will see the machines differ structurally. Replicate there, or record as intentional.
2. **Do not repurpose `/dev/sdc1`** until the new layout has run for a while — it is the rollback.
3. **43% of what migrated gains nothing from ext4** — `agent-worktrees` (27 GB, mostly merged branches) and `phone-media` (28 GB archived media). A worktree sweep would reclaim most of 27 GB.

## Cleanup audit

- **CLEAN** — no agents running; no session-created residue in repos; both trees self-consistent; all merged branches deleted locally and remotely.
- **EXPECTED** — 12 dirty files in workspace-hub (bridge-managed `.claude/memory/*` and generated artifacts); `/mnt/local-analysis` symlink retained by design; NTFS volume retained as rollback.
- **UNEXPECTED** — 57 dirty tracked files in `assetutilities` on a feature branch. **Pre-existing**, observed by a read-only audit agent before this session's work; not touched here. Worth triaging.
