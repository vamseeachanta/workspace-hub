# Archived Skill: `dirty-main-narrow-fix-promotion-with-stash-recovery`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/dirty-main-narrow-fix-promotion-with-stash-recovery`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/dirty-main-narrow-fix-promotion-with-stash-recovery`
Consolidation date: 2026-04-29

---

---
name: dirty-main-narrow-fix-promotion-with-stash-recovery
description: Promote a narrow fix from a feature/worktree into workspace-hub main when main is dirty; verify label taxonomy before issue creation and recover safely when stash reapply conflicts.
version: 1.0.0
author: Hermes Agent
category: workspace-hub-learned
tags: [git, cherry-pick, stash, promotion, workspace-hub, github-issues]
---

# Dirty-main narrow fix promotion with stash recovery

Use when:
- a single verified fix commit must be promoted to `main`
- `/mnt/local-analysis/workspace-hub` `main` is dirty
- you also need to create GitHub issues from generated scripts without trusting assumed labels

## Core lessons
1. Do not cherry-pick onto dirty `main`.
2. Before `gh issue create`, verify exact repo labels; do not assume generic labels like `tests`, `parsing`, or `releases` exist.
3. `git stash push -u` may be the right move for a quick narrow promotion, but `stash apply` can fail after the cherry-pick/push if the restored work overlaps files changed by ongoing local work.
4. If restore fails, keep the stash; do not drop it. Prefer recovery in isolation rather than forcing restore on dirty `main`.

## Issue-creation preflight
Run before creating issues:
```bash
gh auth status
gh label list --repo <owner/repo>
gh issue list --repo <owner/repo> --state all --search '"<exact proposed title>"' --limit 10
```

Rules:
- use only labels that actually exist in the target repo
- exact-title search is cheap and catches obvious duplicates
- if a label is missing, patch the local issue-generation scripts before creation

## Narrow promotion flow from dirty main
1. Inspect dirty state:
```bash
cd /mnt/local-analysis/workspace-hub
git status --short --branch
```

2. Stash tracked + untracked state:
```bash
git stash push -u -m "pre-<commit>-promotion-YYYY-MM-DD"
```

3. Verify clean enough to proceed:
```bash
git status --short --branch
git stash list | head
```

4. Update `main` and verify fix absent:
```bash
git fetch origin --prune
git pull --ff-only origin main
if git merge-base --is-ancestor <commit> HEAD; then echo already-present; else echo absent; fi
```

5. Cherry-pick and validate:
```bash
git cherry-pick <commit>
bash tests/hooks/test-require-plan-approval.sh
git push origin main
```

6. Restore the stash conservatively:
```bash
git stash apply stash^{/pre-<commit>-promotion-YYYY-MM-DD}
```
Use `apply`, not `pop`, so the stash survives failed or partial restore.

## If stash apply fails
Symptoms:
- `Your local changes to the following files would be overwritten by merge`
- promotion already succeeded and pushed

Response:
1. stop immediately
2. confirm the promoted fix is on `main` and pushed
3. confirm the stash still exists with `git stash list`
4. do **not** drop the stash
5. do **not** continue unrelated work from this dirty `main`
6. recover in isolation:
   - preferred: create a recovery branch/worktree from the stash and inspect/merge deliberately
   - avoid repeatedly stacking more stash/apply operations on dirty `main`

## Why this matters
This pattern preserves the narrow promotion audit trail while protecting the original dirty local state. It also avoids GH issue creation failures caused by repo-taxonomy drift between assumed labels and real labels.

## Verification checklist
- `gh auth status` healthy
- exact labels verified in target repo
- duplicate-title search returns no exact matches
- fix commit not already on `main`
- targeted regression test passes after cherry-pick
- push succeeds
- if restore fails, stash still exists and is preserved for isolated recovery
