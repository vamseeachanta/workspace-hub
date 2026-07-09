> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-09
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_sparse_worktree_commit_trap.md

---
name: sparse-worktree-commit-trap
description: "In a sparse-checkout worktree, git add silently skips files outside the cone — verify the COMMITTED tree (git show HEAD), not the working tree, or you ship data loss"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9d5c1253-dc2e-4029-884d-0f22ed116810
---

When committing in a **sparse-checkout worktree**, `git add <path>` **silently refuses** files outside the sparse cone (prints a hint, exits success, stages nothing). A commit then lands *missing those files* even though they exist on disk and the working tree looks correct.

**Why:** llm-wiki#28 pilot (2026-05-27). I built a sparse worktree (excluding the 19K `sources/` dir), Codex generated 44 new chunk pages under `sources-index/` + a test, but those paths were outside my sparse cone. `git add` staged only 3 of 45 files; the pushed commit had the index gutted (21,572 deletions) with **no chunk pages** — real data loss in the committed tree, despite the working tree being complete and all my disk-level verifications passing.

**How to apply:**
- To stage new files outside the cone in a sparse worktree, use **`git add --sparse <path>`**.
- **Verify the committed tree, not the working tree.** Disk-level checks (`cat file`, `find`, running a script) pass even when the commit is incomplete. Run verification against `git show HEAD:<path>` / `git ls-tree -r HEAD` before pushing. This extends [[feedback_subagent_write_phantom]]: not just "did the file land on disk" but "did it land in the commit."
- For agent-generated output (Codex/subagent) verify **set equality of content**, not counts — llm-wiki#28 r1 dropped exactly 2 rows while counts looked plausible; a row-content `diff` (after normalizing any path rewrites) is what exposed it. Counts can coincide; set-diff cannot lie.

**Codex-delegation pilot pattern that worked (llm-wiki#28):** dispatch into an isolated sparse worktree off `origin/main` → Codex implements → Claude r1 set-equality verification catches defect → precise r2 fix dispatched to Codex → re-verify committed tree → `git add --sparse` → PR. See [[feedback_codex_needs_pushed_artifact]], [[feedback_cross_provider_review_payoff]].
