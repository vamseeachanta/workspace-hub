> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-02
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_origin_committed_with_unresolved_markers.md

---
name: Origin committed with unresolved merge markers
description: Parallel session can land half-resolved files containing `<<<<<<< Updated upstream` markers; subsequent merge produces double-nested conflicts; cleanest fix is `git checkout --ours` if HEAD is clean
type: feedback
originSessionId: 73cbf578-6fb3-4436-9a95-06ed471cd8b1
---
A parallel Claude session can commit a half-resolved file containing literal `<<<<<<< Updated upstream` / `=======` / `>>>>>>> Stashed changes` text on origin/main (from a prior `git stash apply` that wasn't completed). When the local session later merges, git produces DOUBLE-NESTED conflict markers:
```
<<<<<<< HEAD
> **Status:** completed
=======
<<<<<<< Updated upstream
> **Status:** plan-review
=======
> **Status:** completed
>>>>>>> Stashed changes
>>>>>>> 8f1aa93c0...
```

**Why:** the outer markers are git's normal HEAD-vs-FETCH_HEAD merge conflict; the inner markers are pre-existing TEXT in origin's committed file (because a prior committer mistakenly committed conflict-marker text without resolving). It happened on 2026-05-01 with `docs/plans/2026-05-01-issue-2570-...md` — origin's `52c1cf09a` had 9 stale markers; the manual run had to resolve via `git checkout --ours` of the file (HEAD was already clean).

**How to apply:** when you see double-nested markers after a pull, FIRST `git --no-optional-locks show origin/<branch>:<path> | grep -nE "^(<<<<<<<|=======|>>>>>>>)"` to confirm origin literally contains the markers. If your HEAD's version is clean (no markers), `git checkout --ours <path>` takes your clean version cleanly. Don't try to merge the inner markers manually — origin's text is broken at HEAD, not just in the merge view.

**Detection signal:** `<<<<<<< Updated upstream` and `>>>>>>> Stashed changes` come from `git stash apply`, not `git merge`. Their presence on origin/main indicates someone committed a stash-apply mid-resolution.
