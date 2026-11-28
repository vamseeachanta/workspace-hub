# File structure: work roots and folder layout

Source of truth: [`file-structure.yaml`](file-structure.yaml). Measured 27 Nov 2026.
Per-machine sizes, paths and the full deviation list are in the private fleet-ops repository
(`docs/knowledge-maps/file-structure.yaml`); this page carries only the machine-neutral part.

## The standard

Each machine has one work root, `W`, on a local disk. A home-folder alias such as `<work root alias>` may
point at it. `W` holds only:

| Entry | Purpose |
|---|---|
| `<registered-repository>/` | The one canonical clone of a registered repository, on lean (post 23 Nov 2026) history |
| `_wt/` | Linked Git worktrees only, each named `<repo-short>--<slug>` |
| `_pm/` | Machine operations: helpers, the pinned `fleet-ops-run` worktree, consistency reports, live desk files |
| `_backups/` | Verified bundles and patches with a `MANIFEST.json`; a second copy lives on another machine |
| `_archive/` | Cold archives with a SHA-256 manifest |
| `.claude/` | Workspace-level Claude configuration |

Scratch goes to the OS temp folder or a repository's git-ignored `.tmp/`. Bulk solver output and
cold reference data go to `${ACE_DATA_ROOT}` with a committed manifest (`DATA_PLACEMENT.md`).
Every repository carries `docs/structure.yaml` and a rendered `docs/STRUCTURE.md`.

Rule files: fleet-ops `intake/cleanup/MACHINE-CLEANUP-PROMPT.md` (Phase 1 item 4),
fleet-ops `machine-manager/WORK-ARCHITECTURE.md` (principles 2 and 3),
`.claude/rules/workstation-hygiene.md`, `docs/standards/DATA_PLACEMENT.md`.
The `W` guide is `config/workstations/ws-structure.yaml`.

"Equal across machines" means `check-work-layout.py` exits 0 on every host and every registered
repository's structure guide reports no undocumented folder. Neither condition had been tested on
any host at measurement: the layout checker is in PR 4537 (open) and the 6-hourly consistency run
(fleet-ops #776, merged 27 Nov) is not yet installed on any host.

## Where things sit that do not belong

Eleven classes of non-standard location were found. Each has one destination.

| Class | Hosts | Destination |
|---|---|---|
| Canonical clone on pre-reset history | 6 | Bundle, re-clone lean; release its worktrees first |
| `*.pre-rollout-*` clone beside the canonical one | 3 | Bundle to `_backups`, retire |
| Second worktree container (`_worktrees`, `_rv`, `_scratch`, job folders) | 6 | `W/_wt`, released by `wt_sweep.py` when landed |
| Mis-named or non-worktree entry in `_wt` | 7 | Rename live worktrees; logs to `_pm`; scratch to OS temp |
| `_scratch`, `_tmp`, `<home>/claude-scratch` | 7 | OS temp or repo `.tmp/` |
| Unregistered folder or loose file at `W` top level | 7 | `_pm`, `_archive`, `${ACE_DATA_ROOT}`, or retire |
| Launcher or control root outside `W` (`ws-pm`, a second `_pm`) | 5 | `W/_pm` |
| Job folders in the home folder | 6 | Retire after the three-layer unmerged-work proof |
| Earlier work root still populated | 3 | `_archive` with manifest after per-clone proof |
| Bulk output inside `W` or at a drive root | 4 | `${ACE_DATA_ROOT}` with manifest and second copy |
| Work root split across two places, or a workspace on a FUSE volume | 2 | Move clones under the agreed `W`; keep the old path as an alias |

The "Hosts" column counts machines out of seven (the Windows solver host, the Windows desk, the first Linux host, the second Linux host, the shared GPU node,
the GPU host, the laptop).

## Deviations

62 deviations across seven machines (64 at the first build; two closed on 28 Nov). Per-host counts
are private. The Windows desk is the closest to the standard: all five reserved folders exist
and its canonical clones are on lean history. The largest volumes sit outside `W` on the Windows solver host and
in earlier work roots on the second Linux host and the GPU host. Detail is private.

## Structure guides

Four of 39 owner repositories carry `docs/structure.yaml` on their default branch:
workspace-hub, digitalmodel, assetutilities and fleet-ops. Public repositories still without one:
aceengineer-website, assethold, deckhand-sandbox, hobbies, raw-to-knowledge-playbook,
worldenergydata, worldenergydata-wiki. 28 private repositories have none. Local clones lag
further, because a pre-reset clone cannot fast-forward to the lean `main` that carries the guide.

## What was not measured, and why

- Sizes on FUSE and network volumes: skipped by design, because `git status` and `du` there can
  stall a whole census (cleanup prompt rule 2). They need their own run.
- Two `_wt` folder sizes: `du` exceeded its 900-second limit.
- Untracked files: the census counted tracked changes only, to keep it fast.
- Processes and scheduled tasks using each folder: not inspected. No folder in this map is judged
  stale on this evidence; removal still needs the cleanup prompt's Phase 1 proof.
- The pre-reset test compares root-commit dates with the lean root seen on other hosts. It is a
  heuristic, not a comparison of commit IDs against origin; no fetch was run on any host.

## Refresh

```
gh api repos/vamseeachanta/<repo>/contents/docs/structure.yaml?ref=<branch> --silent   # guides on origin
uv run python scripts/operations/check-work-layout.py --json --private-config <file>   # per host, after PR 4537
uv run python scripts/operations/check-structure-guide.py <repo> --json                 # per repository
python machine-manager/consistency.py --pinned <sha>                                    # fleet-ops, every 6 h
```

## Open questions

- The private layout file that `check-work-layout.py` reads was not found. Until it exists,
  private repositories cannot be classified as registered.
- fleet-ops `ECOSYSTEM.md` names a helper folder on the Windows solver host that does not exist, and a launcher root
  outside `W`. Which text governs until the move?
- `_wt` names use short prefixes (`fo`, `wh`, `dm`, `wed`) with no registered list.
- `config/workstations/registry.yaml` names an alias path (a link to the work root) as the workspace
  root on one Linux host and a FUSE-mounted folder on the other. It disagrees with `ECOSYSTEM.md` and with the measured roots.
