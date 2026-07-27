> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-26
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_no_materialize_into_foreign_worktree.md

---
name: feedback_no_materialize_into_foreign_worktree
description: "Don't materialize files into a working tree checked out on another session's branch — it pollutes their tree and can leak into the shared index"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f034965f-13d1-4a2f-b6b9-58d211c43da0
---

When the main working tree is on **another session's branch** (e.g. `fix/statusline-codex-quota`, 85 commits behind main) and you're committing via the temp-index technique off `origin/main`, do NOT `git show origin/main:path > path` to materialize files into the working tree for editing/reading. It leaves your changes as modified/untracked files in the other session's tree, and at least once a materialized+edited README **leaked into the shared main index** (showed as staged) — which would have ridden along in the other session's next commit.

**Why:** the temp-index commit (`GIT_INDEX_FILE` read-tree/add/write-tree/commit-tree) is isolated, but the *working tree* edits you make to feed it are NOT — they sit in the shared tree/index until cleaned. Cleanup is fiddly and risks the other session's work.

**How to apply:** to edit/run real code on current `main` while the tree is on a foreign branch, use a dedicated **git worktree** off `origin/main` (accepting the workspace-hub checkout cost) — never edit in the foreign tree. For plan/doc/review artifacts, write them, temp-index commit, then **immediately `rm` the working-tree copies + `git checkout HEAD -- <tracked-file>`** to restore the foreign tree. Verify clean with `git status --short` scoped to your paths before exit. Companion to [[feedback_temp_index_snapshot_live_repo]] and [[feedback_multi_agent_commit_serialization]].
