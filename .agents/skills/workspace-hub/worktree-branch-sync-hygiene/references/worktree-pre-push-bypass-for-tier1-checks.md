# Archived Skill: `worktree-pre-push-bypass-for-tier1-checks`

Original path: `/home/vamsee/.hermes/skills/workspace-hub/worktree-pre-push-bypass-for-tier1-checks`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub/worktree-pre-push-bypass-for-tier1-checks`
Consolidation date: 2026-04-29

---

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
2. the failure is clearly due to missing sibling repos / worktree path assumptions OR unrelated repo-wide pre-push debt
3. the branch is narrow and low-risk (for example a docs/plans-only branch)
4. review evidence is already present for feature/fix commits when applicable

## Important refinement learned in live use

There are actually two distinct failure modes:

1. Clean-worktree topology failure
- the isolated worktree does not contain sibling tier-1 repos under the paths assumed by the pre-push hook
- typical errors are `directory not found` for `assetutilities`, `digitalmodel`, `worldenergydata`, or `assethold`

2. Topology-compatible checkout still blocked
- even after recreating the landing commit in the real workspace checkout (where sibling repos do exist), the same pre-push hook can still block the push because it runs ecosystem-wide tier-1 checks and fails on unrelated repo debt
- observed example: a docs-only branch was blocked by existing `assetutilities` ruff/mypy failures, not by the branch's own diff
- another observed example: after the tier-1 checks, the hook's config-drift step can still fail with `ModuleNotFoundError: No module named 'yaml'` from `scripts/quality/check_config_drift.py`; this is also environment/governance debt unrelated to the narrow branch content

Practical decision rule:
- first try a normal push from a topology-compatible checkout once
- if the original isolated worktree push fails on missing sibling repos, recreate or cherry-pick the narrow commit onto a branch in the real workspace checkout (or another topology-compatible checkout) and try one normal push there
- if that topology-compatible push still fails only because of unrelated ecosystem-wide checks, prefer the audited bypass for the narrow docs-only branch instead of debugging the clean worktree further
- record that the bypass was environmental/governance-driven, not required by the branch content itself

## Recommended branch-recreation sequence for narrow docs-only landings

When a clean integration worktree contains only a narrow docs/plans commit:

1. Create the docs-only commit in the clean worktree.
2. Recreate that commit on a topology-compatible branch in the real workspace checkout (for example by cherry-picking or re-committing the same file) so the hook can at least see the expected sibling repos.
3. Attempt one normal push from that topology-compatible branch.
4. If the push still fails only because of unrelated repo-wide gates (for example existing `assetutilities` ruff/mypy failures or environment debt like missing `yaml` for `check_config_drift.py`), push with:

```bash
GIT_PRE_PUSH_SKIP=1 git push -u origin <branch-name>
```

5. Keep the resulting commit/branch narrow and auditable, and then open the PR from that pushed branch.

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
