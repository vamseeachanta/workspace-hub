> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_merge_race_silent_revert.md

---
name: Merge-race silent revert
description: Under aggressive auto-sync, `git merge --no-ff` followed by `git commit --no-edit` after a HEAD-lock failure can produce a merge commit that records the correct parents but silently drops the second-parent's tree; always verify merged content matches the branch tip
type: feedback
originSessionId: ac348218-fd8d-49f9-b0d4-daa28cc4ba54
---
When `git merge --no-ff` fails with `fatal: update_ref failed for ref 'HEAD': cannot lock ref 'HEAD'`, the merge strategy has already computed the tree and staged it, but the HEAD update itself lost a race with another process. If you then run `git commit --no-edit` to finalize, git commits whatever is currently in the index — which, if auto-sync committed additional files in the interim, will be a stale index that no longer matches the merge-strategy's output. The resulting merge commit has correct parents (so `git log --graph` looks fine), but the tree silently reverts the second-parent's contributions.

**Why:** The workspace-hub repo has an aggressive auto-sync daemon that fires `git commit` whenever it detects file changes in config/reports/state paths. During a multi-step merge sequence, it can fire between the merge-tree computation and the HEAD update, invalidating the staged tree.

**How to apply:**
- After *every* merge on workspace-hub's main, verify the merged file content matches the source branch tip, not just that the merge commit exists. Compare line counts or blob SHAs for the deliverable files. Do not trust `git log --graph` alone.
- If the verification fails, restore content directly from the source branch (`git checkout <branch> -- <files>`) and commit with an explicit "restore — prior merge silently reverted content" message. The merge commit parents stay correct; the restore commit sits on top.
- Prefer cherry-pick over merge when blast radius matters — cherry-pick preserves the file-level intent even if HEAD races, because it commits explicit file content rather than a tree computed from parents.
- When multiple merges are queued, run them *immediately* back-to-back in one `set -e` script. Gaps between merges invite auto-sync interference.
- When status shows `M `/`A ` entries you didn't create, that's auto-sync. Safest path: `git checkout HEAD -- <file>` on any specific file that blocks a merge rather than stashing the whole tree.
