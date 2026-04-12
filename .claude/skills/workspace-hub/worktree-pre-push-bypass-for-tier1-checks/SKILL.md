---
name: worktree-pre-push-bypass-for-tier1-checks
description: Handle workspace-hub integration-branch pushes from isolated git worktrees when the pre-push hook incorrectly assumes sibling tier-1 repos exist under the worktree path.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Worktree Pre-Push Bypass for Tier-1 Checks

Use when pushing a new branch from a workspace-hub git worktree and `git push` fails before network push because `.git/hooks/pre-push.sh` tries to run tier-1 repo checks against sibling directories that do not exist inside the worktree.

## Trigger symptoms

Typical push failure output includes lines like:
- `New branch — running all tier-1 repo checks.`
- `ERROR: directory not found: /.../worktree/.../assetutilities`
- `ERROR: directory not found: /.../worktree/.../digitalmodel`
- `ERROR: Unknown repo 'OGManufacturing'`
- `failed to push some refs`

This happens especially for isolated integration worktrees such as:
- `workspace-hub-integration-*`
- other temporary review/landing worktrees created from `main`

## Root cause

`workspace-hub/.git/hooks/pre-push.sh` treats a new-branch push as `RUN_ALL=true` and then checks the full tier-1 repo list. In an isolated worktree, those repos are not present as sibling directories, so the hook fails before the branch can be pushed.

The hook already provides a soft bypass:
- `GIT_PRE_PUSH_SKIP=1`

and logs the bypass to:
- `logs/hooks/pre-push-bypass.jsonl`

## Safe workaround

From the integration worktree, push with the documented soft bypass:

```bash
cd /mnt/local-analysis/worktrees/<worktree-name>
GIT_PRE_PUSH_SKIP=1 git push -u origin <branch-name>
```

Expected output includes:
- `[pre-push] GIT_PRE_PUSH_SKIP=1 — bypass logged to .../logs/hooks/pre-push-bypass.jsonl`

Use this only when:
1. you already ran targeted validation in the clean worktree
2. the failure is clearly due to missing sibling repos / worktree path assumptions
3. review evidence is already present for feature/fix commits

## Verification before bypassing

Run at minimum:

```bash
git status --short
git --no-pager log --oneline -5
uv run pytest <targeted test set> -q
```

For combined landing branches, record the exact passing command set in a runbook before pushing.

## After push

1. Save the branch/PR URL.
2. Post GitHub closeout comments with validation evidence.
3. Close landed issues only after the branch is pushed and evidence is posted.
4. Create or link a follow-up issue to fix the pre-push hook itself.

## Permanent fix path

Do not rely on the bypass as the long-term solution. Create/follow a harness issue to make the pre-push hook worktree-aware. In this session, that follow-up was:
- `#2203` — make pre-push tier-1 repo checks worktree-aware for integration branches

## Notes

- This is a workspace-hub-specific operational workaround, not a generic git-worktree pattern.
- Prefer fixing the hook over using repeated bypasses.
- If the hook failure is due to real test/review failures rather than missing sibling repos, do not bypass.
