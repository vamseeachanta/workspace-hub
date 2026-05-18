# Detached HEAD Closeout With Staged Work

Use when an issue worktree has validated/staged changes but `git status -sb` reports `## HEAD (no branch)`.

## Pattern

1. Do not commit blindly from detached HEAD unless you have already chosen an explicit push ref.
2. Run writer/lock preflight before any branch attachment, switch, commit, or push.
3. Capture the intended staged file list before changing branch state:
   - `git status --short`
   - `git diff --cached --name-only`
   - optional: `git diff --cached --stat`
4. Verify the detached HEAD is actually contained by the intended target branch:
   - `git branch --contains HEAD`
   - `git rev-parse --abbrev-ref HEAD`
5. If HEAD is contained by the intended branch and staged files are the intended issue files, prefer attaching to the branch before commit:
   - `git switch <target-branch>`
   - immediately re-check `git status --short` and `git diff --cached --name-only`
6. If staged state changed or branch switch is unsafe, stop and use a temporary branch/worktree route instead of forcing it:
   - `git switch -c closeout/<issue-or-topic>` from detached HEAD, then commit and push that branch for merge/cherry-pick.
7. After commit, verify:
   - `git rev-parse --short HEAD`
   - `git status --short`
   - `git ls-remote origin <target-branch>` after push.

## Pitfall

The dangerous state is not detached HEAD itself; it is committing validated staged work onto a commit that is not attached to the intended branch/ref and then reporting closeout without verifying the pushed ref. Treat branch attachment/ref selection as part of the commit gate.