---
name: targeted-artifact-commit-verification
description: Verify whether the exact files from a just-completed task are still uncommitted before creating another commit, especially in dirty repos with unrelated churn.
version: 1.0.0
tags: [git, commit, verification, dirty-repo, handoff]
---

# Targeted Artifact Commit Verification

Use when:
- the repo has lots of unrelated modified/untracked files
- the user asks to commit work from the current task
- you need to avoid creating a duplicate/no-op commit
- you suspect an auto-sync or prior commit may have already landed the exact artifacts

## Why this exists
In a dirty checkout, `git status --short` alone can mislead you into thinking your task artifacts still need committing when only unrelated files remain dirty.

A reliable pattern is to verify the exact task artifact set before staging or committing.

## Workflow

1. Identify the exact task files.
   Example:
   - `analysis/provider-session-ecosystem-audit.json`
   - `docs/reports/provider-session-ecosystem-audit.md`
   - `docs/reports/2026-04-23-provider-session-learning-transfer.md`

2. Check only those files for remaining diff.
   Run:
   - `git status --short -- <files...>`
   - `git diff --stat -- <files...>`

3. If both are empty, do not create a new commit yet.
   Treat this as a possible already-committed state, not a failure.

4. Confirm the files are tracked and identify the commit that already contains them.
   Run:
   - `git ls-files --error-unmatch <files...>`
   - `git log --oneline -n 5 -- <files...>`
   - if needed, `git show --stat --name-only --oneline <sha> -- <files...>`

5. Only create a new commit if the targeted files still have real uncommitted changes.

## Exit/handoff extension
If the target artifacts are already committed but the repo is still dirty:
- explicitly tell the user the requested task artifacts are already committed
- name the commit SHA and subject
- distinguish unrelated remaining churn from the completed task artifacts
- if the user asks to prepare for exit, create a handoff doc rather than forcing another commit for the same files

## Recommended wording
- "The files from this task are already in commit `<sha>`; there is no remaining diff for them."
- "The repo is still dirty, but the remaining changes are unrelated to the completed artifact set."

## Pitfalls
- Do not rely on repo-wide `git status` when the task only touched a few files.
- Do not create a second commit just because the worktree is dirty.
- Do not assume a newly written file is uncommitted; auto-sync or a prior commit may already include it.
