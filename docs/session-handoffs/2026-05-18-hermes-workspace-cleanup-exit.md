# Session Handoff — Hermes workspace cleanup and exit

- **Timestamp:** 2026-05-18T17:05:27Z / 2026-05-18T12:05:27-05:00
- **Host:** ace-linux-1
- **Repo:** `/mnt/local-analysis/workspace-hub`
- **Branch:** `main`
- **Purpose:** durable closeout after workspace cleanup, stash disposition, and exit-state verification.

## Current outcome

Completed cleanup of the primary workspace-hub checkout:

1. Preserved and committed durable review/cleanup artifacts in earlier commits:
   - `b8377fd3f chore: preserve review and cleanup evidence`
   - `850880ad7 chore: record skill patch ledger`
2. Auto-sync advanced `main` afterward:
   - `505441c29 chore(sync): auto-sync 2026-05-18`
3. Classified remaining stashes as obsolete safety/runtime/bridge stashes, exported them off-repo for recovery, and dropped live stash refs.
4. Moved untracked issue-2657 patch evidence out of the repo into the preserved cleanup archive.
5. Restored runtime session-signal dirt before closeout.

## Stash disposition

`git stash list --date=iso` is empty after cleanup.

Exported stash/archive evidence lives under:

`/mnt/local-analysis/preserved-workspace-hub-cleanup/2026-05-18/stashes`

Checksums captured during cleanup:

```text
2fa9152e3519250365b3035c0f03e95f544983069682f98cefabf4bdbbaddbf8  stash__0_-e53c71c2e984f72a02390b4ba049cff595c6e830.patch
884c2974501ccc135540882108cb0930bbc937da47d10c34d9d87796e9b612b0  stash__1_-9e215d7ac0ac7c69d05e2ee67e81d7b7d82b34c3.patch
e130e0d7a592ddf6fea0370f0631ef926faac2954624e8d5549a806921fb8792  issue-2657-worktree-stash-2026-05-18.patch
```

Earlier large preserved patch remains outside the repo:

`/mnt/local-analysis/preserved-workspace-hub-cleanup/2026-05-18/llm-wiki-outside-stash-2026-05-18.patch`

- Size observed earlier: `22085094` bytes
- SHA256 observed earlier: `d5bc03c7d1f3d37ca53b6b5cc2f273934d830ac1f04205cf0ca725053fd9ec95`
- Note: mount permissions did not honor `chmod 600`; treat this as locally preserved but not permission-hardened by filesystem mode.

## Primary repo proof before this handoff commit

Live evidence captured at 2026-05-18T12:04:23-05:00:

```text
git status --porcelain=v1 --branch
## main...origin/main
 M logs/orchestrator/hermes/skill-patches.jsonl
?? .claude/skills/workspace-hub-learned/git-operation-serialization-preflight/references/
?? .claude/skills/workspace-hub-learned/llm-wiki-ecosystem-gap-to-issues/references/public-graph-manifest-validation.md
```

```text
git rev-parse HEAD
505441c29617d7a2d7c52cddaf3e69459bc7a980

git rev-parse origin/main
505441c29617d7a2d7c52cddaf3e69459bc7a980

git ls-remote origin refs/heads/main
505441c29617d7a2d7c52cddaf3e69459bc7a980	refs/heads/main

git rev-list --left-right --count HEAD...origin/main
0	0
```

Dirty-state classification before this handoff commit:

- `logs/orchestrator/hermes/skill-patches.jsonl`: durable skill-patch ledger entries generated after auto-sync; include in closeout commit.
- `.claude/skills/workspace-hub-learned/git-operation-serialization-preflight/references/`: durable skill reference files for detached-head closeout and stash export/drop cleanup; include in closeout commit.
- `.claude/skills/workspace-hub-learned/llm-wiki-ecosystem-gap-to-issues/references/public-graph-manifest-validation.md`: durable skill reference file; include in closeout commit.

## Existing worktrees

Worktrees were inspected, not removed.

### `/mnt/local-analysis/worktrees/workspace-hub-2727`

```text
git -C /mnt/local-analysis/worktrees/workspace-hub-2727 status --porcelain=v1 --branch
## HEAD (no branch)
A  docs/architecture/data-boundary-violations-and-gaps.md
A  docs/architecture/data-layer-contract.md
A  docs/architecture/data-source-inventory.md
A  docs/architecture/followups/issue-canonical-llm-wiki-repo-placement.md
A  docs/architecture/followups/issue-migrate-ace-data-alias.md
A  docs/architecture/llm-wiki-data-promotion-gates.md
A  tests/architecture/test_data_layer_contract.py
A  tests/fixtures/architecture/data_promotion_cases.yaml
A  tests/fixtures/architecture/data_source_inventory.yaml
```

- `HEAD`: `b93dcc68dc94ae0670948a437cdbd1b08bc789a3`
- Branch: detached HEAD
- Stashes: none
- Disposition: preserved. Contains staged issue #2727 data-layer architecture work and must not be removed as part of generic exit cleanup.

### `/tmp/wh-h4`

```text
git -C /tmp/wh-h4 status --porcelain=v1 --branch
## dispatch/h4-2152...origin/dispatch/h4-2152
```

- `HEAD`: `a18c5ef868716f3657aa64d721f9636942a11c36`
- Branch: `dispatch/h4-2152`
- Stashes: none
- Disposition: preserved. Clean dispatch worktree; not removed during this closeout.

## External-action status

No external send/action was performed during this closeout. No Telegram/Hermes remote machine commands were triggered during the cleanup/exit sequence.

## Restart notes

If resuming from here:

1. Start with live repo state, not this static snapshot:
   - `git fetch origin main`
   - `git status --porcelain=v1 --branch`
   - `git stash list --date=iso`
   - `git worktree list --porcelain`
2. If working on issue #2727, inspect `/mnt/local-analysis/worktrees/workspace-hub-2727` first because it contains staged detached-HEAD architecture/test files.
3. If recovering dropped stash content, use the preserved patch archive under `/mnt/local-analysis/preserved-workspace-hub-cleanup/2026-05-18/stashes` rather than `git stash`.
4. Do not run the heavyweight comprehensive-learning pipeline in-session; nightly learning should handle deeper extraction.

## Final proof placeholder

This handoff must be committed and pushed, then final live proof should be reported in the chat response after re-fetching origin.
