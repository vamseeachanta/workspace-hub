# Archived Skill: `targeted-artifact-commit-verification`

Original path: `/home/vamsee/.hermes/skills/development/targeted-artifact-commit-verification`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/development/targeted-artifact-commit-verification`
Consolidation date: 2026-04-29

---

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

## Locked, contended, or post-handoff checkout fallback
If the active checkout is dirty, locked, has long-running git/pre-push/status processes, or the session was interrupted/compacted during commit-push closeout, do not force-remove locks or blindly create another commit just to land/verify a narrow artifact set.

First verify whether the exact target files already landed, even if the latest commit subject looks unrelated or surprising. Auto-sync, stash-recovery, or another handoff process may have committed the correct files under an unexpected message.

Recommended sequence:
1. Check the target files only:
   - `git status --short -- <files...>`
   - `git diff --stat -- <files...>`
2. Inspect recent commits for those exact paths, not just commit subjects:
   - `git log --oneline -n 8 -- <files...>`
   - `git show --stat --name-only --oneline -n 1 <candidate-sha> -- <files...>`
3. Verify remote sync before deciding a new implementation commit is needed:
   - `git rev-list --count @{u}..HEAD`
   - `git rev-list --count HEAD..@{u}`
   - `git rev-parse --short HEAD`
4. If the implementation files are already present on `origin/main`, treat the implementation as landed and do not duplicate it. Only commit any remaining local delta if it is a narrow hygiene change required by repo gates, such as whitespace normalization in review artifacts.
5. If the active checkout is too contended to inspect safely, use a fresh clone or separate clean worktree:
   - `git clone <repo-url> /tmp/<repo>-verify` or use an existing clean worktree.
   - `git show --stat --oneline <candidate-sha> -- <files...>`
   - `git log --oneline -n 5 -- <files...>`
   - direct content grep/read checks for the expected new lines.
6. If the exact files are already present on `origin/main`, post the GitHub/exit note with the actual landing commit and leave unrelated local churn alone.
7. Only create a new commit from a clean checkout if the target files are not already landed remotely and the write surface is narrow enough to avoid contention.

Post-handoff hygiene pattern:
- If `git diff --cached --check` previously failed on archived review Markdown, it is safe to strip trailing whitespace/extra EOF blank lines in those review artifacts and commit that as a narrow cleanup after confirming the functional implementation already landed.
- Keep the closeout comment honest by naming both commits when applicable: the implementation landing commit and the cleanup commit.

## Recommended wording
- "The files from this task are already in commit `<sha>`; there is no remaining diff for them."
- "The repo is still dirty, but the remaining changes are unrelated to the completed artifact set."

## Pitfalls
- Do not rely on repo-wide `git status` when the task only touched a few files.
- Do not create a second commit just because the worktree is dirty.
- Do not assume a newly written file is uncommitted; auto-sync or a prior commit may already include it.
