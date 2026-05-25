---
name: git-commit-pathspec-ignores-staged-deletion
description: "git commit -- <path> is pathspec mode (re-derives from working tree), so it silently ignores a staged `git rm --cached` deletion when the file still exists on disk"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1410bc2-cb05-420e-a38f-5b6ace4a58c7
---

`git commit -- <path>` runs in **pathspec mode**: it re-derives the change from the *working tree*, NOT the staged index. So if you `git rm --cached .env` (untrack but keep the local file) and then `git commit -- .env`, git sees `.env` still present on disk, concludes "no changes," and **silently drops the staged deletion** — leaving the secret tracked. Exit code can still be 1 with "no changes added to commit" while HEAD doesn't move.

**Why:** nearly left a previously-committed `.env` tracked during sabithaandkrishnaestates secret-cleanup (2026-05-23) despite repeated commit attempts.

**How to apply:** to commit a `--cached` removal of a file you intend to keep on disk, commit the **index** (`git commit` with NO pathspec), guarded so only the intended path is staged:
```
git rm --cached --ignore-unmatch .env
[ "$(git diff --cached --name-only)" = ".env" ] && git commit -m "..." || echo ABORT
```
The guard prevents sweeping parallel-session staged changes (cousin of [[feedback_retry_loop_sweep_contamination]]). Related: a timeout-killed `git commit` can leave a staged deletion uncommitted even though HEAD didn't move — re-verify `git ls-files`/`git diff --cached` before retrying (see [[feedback_reflog_as_ground_truth]]). Also: `.env.*` ignore patterns match `.env.example`; add `!.env.example` to keep the template trackable.
