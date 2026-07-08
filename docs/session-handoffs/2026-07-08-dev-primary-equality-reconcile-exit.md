# Session handoff — dev-primary equality reconcile

**Date:** 2026-07-08  
**Box:** `ace-linux-1` / `dev-primary`  
**Repo:** `workspace-hub`  
**Exit time:** 2026-07-08T14:18:41-05:00  
**Purpose:** close out the dev-primary machine-equivalence repair session and leave a clean restart point.

## Current state

- `workspace-hub` is clean and synced: `HEAD == origin/main == 720476822`.
- Latest pushed commit is `720476822 chore(equality): publish equality artifacts from ace-linux-1`.
- The dropped curation state was recovered and is now present on `main` as `fcfde6fd8 chore(curation): refresh dev-primary state`.
- `uv run --script scripts/readiness/build-equality-matrix.py --json --machine dev-primary` now reports:
  - `compute`: `CONFORMS`
  - `data_access`: `CONFORMS`
  - `solvers`: `CONFORMS`
  - `session_curation`: `CURATED-FRESH`
  - `memory_freshness`: `MEMORY-FRESH`
  - provider harness capability rows: `PARITY`, except Gemini skill invoke is `EXPECTED-DIVERGENCE`.
- `STALE-CHECKOUT` is cleared for dev-primary.

## What happened

The first curation run produced local commit `861614515 chore(curation): refresh dev-primary state`, but `git push` was rejected because `origin/main` advanced. Equality was then run while `861614515` was still local-only. That produced an equality evidence file stamped with:

```yaml
checkout_sha: "861614515"
dirty: true
ahead_main: 1
```

That evidence was valid for the moment it was collected, but bad for equivalence reporting. It caused every dev-primary matrix cell to grade `STALE-CHECKOUT`.

The repair was to recover the curation commit from reflog, push it via a clean mainline replay, then run equality only after `HEAD...origin/main` was `0 0`.

## Preserved residue

Do not drop these until a later explicit cleanup pass:

- Branch `preserve/dev-primary-dropped-curation-861614515-20260708T190555Z` -> `861614515`
- Branch `preserve/dev-primary-post-cron-wedge-20260708T013331Z` -> `95ef41333`
- Branch `preserve/dev-primary-main-wedge-20260707T153931Z` -> `ec9c249a8`
- Stash `stash@{2026-07-08T14:07:14-05:00}` — untracked residue before curation replay.
- Older stashes still present:
  - `stash@{2026-07-07T20:33:44-05:00}`
  - `stash@{2026-07-07T10:43:38-05:00}`
  - `stash@{2026-07-06T14:28:19-05:00}`

The newest stash contains generated equality, curation, provider dashboard, and report deltas. It was intentionally preserved rather than dropped.

## Cleanup audit at exit

Verdict buckets:

- **CLEAN:** `workspace-hub` tracked working tree is clean and synced after this handoff commit.
- **EXPECTED:** the preserve branches and stashes listed above are intentional safety nets from the equality/curation replay.
- **DEFER:** `/mnt/local-analysis/.cleanup-trash/20260616-095709` still exists from an earlier cleanup pass.
- **DEFER:** `/tmp` contains recent unrelated artifacts such as `wo-june-2026-*`, `codex-plan-907*.log`, `wed-na-kika-drive-search*.err`, `wt-1296/`, and the active `publish-equality-ace-linux-1.lock`.
- **DEFER:** `/mnt/local-analysis` has many legitimate sibling repos/worktrees plus older top-level reports/artifacts. Do not dispose of these opportunistically; use the repo-ecosystem hygiene workflow if cleanup is desired.

No destructive cleanup was performed in this closeout.

## Remaining matrix gaps

These are no longer checkout contamination:

- `harness`: `DIVERGES`
- `memory`: `NO-MAJORITY`
- `behavior`: `DIVERGES`
- `scheduler`: `DIVERGES`
- `skill_currency`: `EXPECTED-DIVERGENCE`

The same divergence family appears across multiple machines, so refresh peer reports first before changing dev-primary config.

## Recommended next actions

1. Refresh peer evidence before local config edits:

```bash
cd /mnt/local-analysis/workspace-hub
bash scripts/readiness/reconcile-ecosystem.sh --json
```

2. On dev-secondary and Windows boxes, re-run their equality collectors from clean synced checkouts.

3. Only after peer reports are fresh, inspect any persistent `harness`, `behavior`, or `scheduler` divergence as real config drift.

4. File or fix the workflow defect: `curate-session-memory.sh` refreshes tracked curation state but does not itself publish those state files to `main`; running equality before the curation commit lands can publish a self-stale equality report. The operational rule for now is: after curation commits, push/rebase first, verify `git rev-list --left-right --count HEAD...origin/main` is `0 0`, then run equality.

5. Separately audit `scripts/cron/setup-cron.sh --check`; during this session it installed four crontab entries, so the flag is not dry-run behavior.

## Suggested skills

- `workspace-hub/ecosystem-equivalence-reconcile`
- `workspace-hub/repo-ecosystem-hygiene`
- `diagnose`
- `coordination/pre-completion-cleanup-audit`

## Exit checkpoint commands

```bash
cd /mnt/local-analysis/workspace-hub
git status --short --branch
git rev-list --left-right --count HEAD...origin/main
uv run --script scripts/readiness/build-equality-matrix.py --json --machine dev-primary
git stash list --date=iso-strict | sed -n '1,20p'
git branch --list 'preserve/dev-primary*' --sort=-committerdate
```
