> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-27
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_delete_branch_closes_stacked_child_pr.md

---
name: feedback_delete_branch_closes_stacked_child_pr
description: "Merging a stacked parent PR with --delete-branch auto-CLOSES the child PR (not retarget); merge parent WITHOUT delete, retarget child to main, then delete"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad5ef142-80b1-4f1e-b3bc-4d162ec58029
---

Merging a stacked PR with `gh pr merge <parent> --merge --delete-branch` **deletes the head branch immediately**, and when that head is *also the base of another open PR*, GitHub cannot retarget the child in time and **CLOSES the child PR** (state=CLOSED, mergedAt=null) instead of moving it to main. The child then can't be reopened (`reopenPullRequest` / base-branch-edit both fail: "Cannot change the base branch of a closed pull request" / "Could not open the pull request") because its base ref is a 404. Same failure class as [[feedback_squash_merge_breaks_stacked_prs]].

**Why:** `--delete-branch` fires before the retarget. No child should point at a branch you're deleting.

**How to apply — safe stacked-merge protocol (bottom-up):**
1. Merge the parent with `--merge` **and NO `--delete-branch`** (keep the branch alive so the child's base stays valid).
2. `gh pr edit <child> --base main` to retarget the child (it goes CLEAN in ~1 poll once parent content is on main; child diff collapses to its own files only).
3. Merge the child; only `--delete-branch` on the LAST PR that has no remaining children.
4. Delete leftover intermediate branches manually via `gh api -X DELETE repos/<repo>/git/refs/heads/<branch>` after everything's merged.

**Recovery if a child already got auto-closed:** head branch commits are NOT lost (branch still exists). Can't reopen — instead `gh pr create --base main --head <child-branch>` as a fresh PR ("Supersedes #<old>"), merge WITHOUT delete if a further child still bases on it, then continue. Verified 2026-07-12 on aceengineer-website: #57 merge with --delete-branch closed #58 → recovered #58 as #60 → retargeted #59 to main → all landed. See [[project_aceengineer_website_redesign_subsea7]].
