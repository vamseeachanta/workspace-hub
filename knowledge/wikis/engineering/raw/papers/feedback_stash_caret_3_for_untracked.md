> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_stash_caret_3_for_untracked.md

---
name: Extract untracked files from a `-u` stash via the third parent
description: `git checkout stash@{0} -- <path>` silently fails (`pathspec did not match`) for files that were untracked when stashed; their content lives at `stash@{0}^3`, the untracked-files commit
type: feedback
originSessionId: 68238359-8235-44a3-bdd9-b90342e2bd73
---
A stash created with `git stash push -u` is internally a merge commit with up to three parents: `^1` is HEAD-at-stash-time, `^2` is the index-at-stash-time, and `^3` is a tree of untracked files (only present when `-u` was passed). The main `stash@{0}` tree only contains the tracked-then-modified files; untracked files do *not* appear in it. So `git checkout stash@{0} -- <untracked-path>` exits with `pathspec '<path>' did not match any file(s) known to git` even when the file is clearly visible in `git stash show -u`.

**Why:** `git stash show` and `git stash show -u` query different parts of the stash structure, which is why the file appears in one listing but not the other. The `^3` commit is the canonical location for stashed untracked content, but it's not part of the stash's "main" tree, so most stash-aware commands don't see it without explicit dereferencing.

**How to apply:**
- To extract a single untracked file from a stash without `stash pop` (avoiding all the conflict risk of pop, which is the common failure mode under workspace-hub's continuous auto-sync activity): `git checkout stash@{0}^3 -- <path>`. The file appears in the working tree *and* is auto-staged.
- To verify `^3` exists before trying: `git rev-parse stash@{0}^3` (errors if `-u` wasn't used during the original stash).
- To list what untracked content lives in the stash: `git ls-tree -r stash@{0}^3` or `git stash show -u stash@{0} --name-only`.
- To dump file content directly to stdout (e.g., for inspection without modifying the working tree): `git show stash@{0}^3:<path>`.
- This is the safest single-file extraction path when `stash pop` would conflict with the working tree.
