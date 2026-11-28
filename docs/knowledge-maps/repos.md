# Repositories map (public layer)

Source of truth: `repos.yaml` beside this file. Verified 2026-11-27 15:48Z.
Private detail (all repositories, clone paths, per-machine state, deviations):
fleet-ops `docs/knowledge-maps/repos.yaml` (private repository).

## What the map holds

- The catalogue of the 12 public repositories under the owner account: purpose,
  default branch, owner lane, and the root commit of origin's default branch
  after the 23 Nov 2026 lean reset.
- The standard that defines "equal across machines" for clones.
- Exact, machine-neutral commands to refresh every figure.
- Counts only for the private side: 51 repositories in all, 39 private,
  12 archived.

## Counts (2026-11-27)

| Measure | Value |
|---|---|
| Repositories under the owner account | 51 |
| Public / private | 12 / 39 |
| Archived | 12 |
| Default branches with a 23 Nov 2026 "Fresh start" root | 27 |
| Machines scanned | 7 |
| Clones found (a `.git` directory, not a worktree) | 207 |
| Clones still on pre-reset history | 83 |
| Deviations recorded in the private map | 134 |

## Public repositories

| Repository | Purpose | Default | Lean reset | Origin root | Owner lane | Machines with a clone |
|---|---|---|---|---|---|---|
| workspace-hub | Shared base on every machine: rules, fleet scripts, configuration, AI account collector | main | 2026-11-23-lean | c3380a99245a | platform team | 7 |
| digitalmodel | Offshore engineering calculations: strength, fatigue, fitness for service, hydrodynamics | main | 2026-11-23-lean | 5d3f3c9f9380 | engineering models team | 7 |
| worldenergydata | Public energy data library: BSEE, EIA, economics, safety and production analyses | main | 2026-11-23-lean | 4896175b44b5 | energy data team | 7 |
| worldenergydata-wiki | Public wiki of US federal energy data (BSEE, NOAA, USGS, MMS) | main | 2026-11-23 | c9711963dc18 | unassigned (inferred: energy data team) | 7 |
| assetutilities | Shared utility library for the engineering and business repositories | main | 2026-11-23-lean | 3312f13e56b4 | unassigned (inferred: platform team) | 6 |
| assethold | Stock analysis and guidance for long-term holdings | main | 2026-11-23-lean | 424d43a4a8b7 | owner stream; no team named | 6 |
| raw-to-knowledge-playbook | Public method for turning raw archives into verified, citable knowledge | main | 2026-11-23 | c878d45ed1a4 | unassigned (inferred: knowledge team) | 6 |
| aceengineer-website | Public company site: capability pages, case studies, articles | main | 2026-11-23-lean | cf9611c6f0b4 | website team | 5 |
| deckhand-sandbox | Public open-tier sandbox for Deckhand | main | 2026-11-23 | a9a59508530b | Deckhand team (retired stream) | 1 |
| hobbies | Personal hobby projects | main | 2026-11-23 | 53a5c21c598e | owner (personal) | 1 |
| kaggle-rogii-2026 (archived) | Kaggle wellbore geology prediction entry | main | 2026-11-23 | b85f2755c2e3 | none | 1 |
| pdf-large-reader (archived) | Memory-efficient PDF processing library | master | not reset | 4644f14058c0 | none | 0 |

Table: public repositories, 2026-11-27. "Origin root" is the first 12 hex of
`git rev-list --max-parents=0 origin/<default>`. Lanes come from the road-map
index; "inferred" means no road map names a team.

## The standard: one canonical clone per repository per machine

Rules: `.claude/rules/workstation-hygiene.md`, `.claude/rules/merge-cleanup.md`
and the fleet rule "after a lean reset, never work or pull from an old clone"
(fleet-ops issue #691, private). A machine meets the standard for a repository
when all of these hold:

1. Exactly one canonical clone, at `<W>/<repo>`.
2. Its HEAD root commit equals origin's default-branch root. A clone made
   before the 23 Nov reset fails this, even after a fetch, because its local
   branch still sits on the old history.
3. It is on its default branch, clean, with no stash, and not behind origin
   after a fetch.
4. Every other line of work is a linked worktree under
   `<W>/_wt/<repo-short>--<slug>`; `<W>/_wt` holds no full clones.
5. No `<repo>.pre-rollout-*` copies remain once their local-only work is
   bundled with `--all` and restore-tested.
6. Placement rules hold (for example, a personal-records repository stays on
   one named machine).

The standard does not require every machine to hold every repository. No
per-host list of required repositories is on `main`, so a missing clone is not
reported as a deviation.

## Why the pre-reset check matters

A rebase or pull from a pre-reset clone can replay the old history onto the new
root and push it back. The lean reset kept the old history in two verified
archives, so a pre-reset clone holds no history that is otherwise lost; the
only content at risk is work that exists in that clone alone (unpushed
commits, worktrees, stashes, uncommitted files). That content is bundled and
restore-tested before the clone is replaced.

## How to refresh

All commands are read-only. The scan makes no fetch, so "behind" is measured
against each clone's last fetch.

- Catalogue: `gh repo list vamseeachanta --limit 200 --json name,visibility,isArchived,defaultBranchRef,pushedAt,description`
- Origin root without a clone: page through
  `gh api 'repos/vamseeachanta/<repo>/commits?sha=<default>&per_page=1'`
  to the `rel="last"` page and read `.[0].sha`.
- Origin root from a clone: `git -C <W>/<repo> rev-list --max-parents=0 origin/<default>`
- Clone root: `git -C <clone> rev-list --max-parents=0 HEAD`
- Ahead/behind: `git -C <clone> rev-list --left-right --count HEAD...@{u}`
- Dirty: `GIT_OPTIONAL_LOCKS=0 git -C <clone> status --porcelain | wc -l`
- Linked worktrees: `git -C <clone> worktree list --porcelain | grep -c '^worktree '`, minus 1
- Stash: `git -C <clone> stash list | wc -l`
- Find clones: `find <W> -maxdepth 3 -name .git -type d` (a `.git` directory is
  a clone; a `.git` file is a worktree and is not counted twice).

## What was not measured

- Machines outside the seven listed (the first additional Windows host, the second additional Windows host) were not scanned.
- Clones deeper than three levels under `<W>`, or deeper than one level under a
  home folder, were not searched.
- No fetch was run, so "behind" can understate the true gap on a clone that has
  not fetched recently; the private map records each clone's fetch age.
- Owner lanes for assetutilities, worldenergydata-wiki and
  raw-to-knowledge-playbook are inferred.
