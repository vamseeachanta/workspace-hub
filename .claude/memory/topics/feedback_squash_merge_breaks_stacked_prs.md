> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-18
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_squash_merge_breaks_stacked_prs.md

---
name: feedback_squash_merge_breaks_stacked_prs
description: Squash-merging a base PR auto-closes/conflicts its stacked child PRs; consolidate additive lanes into one PR
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a3f0b660-13f8-48d8-aad2-8b2f5c2df93b
---

When PRs are stacked (child PR based on a parent feature branch) and the parent is
**squash-merged with `--delete-branch`**, two things break at once:
1. Children targeting the now-deleted parent branch are **auto-CLOSED** by GitHub
   (can't reopen — base branch is gone) → must open NEW PRs from the same head
   branch targeting `main`.
2. Squash creates a *new* commit on main, so the child's history (containing the
   parent's original commit) **conflicts** with main. Fix = `git merge origin/main`
   into the child (NOT rebase — rebase needs a force-push, which is auto-denied),
   resolve, normal push.

**Why:** these are additive lanes all editing the SAME file region (e.g. the
`__init__.py` export list / `__all__`). Even after each is made mergeable vs main
individually, merging the first changes main → the rest re-conflict on that same
region. Sequential merges = repeated re-syncs.

**How to apply:** for N finished, verified, additive lanes off one spine — after
the spine merges, **consolidate the N lanes into ONE integration PR** with a single
reconciled shared file (merge them together locally, resolve the export list once,
run the full test suite, push, open one PR that `Closes #a, #b, #c`, close the
redundant per-lane PRs pointing to it). One clean merge, zero re-conflicts. The
per-issue split still did its job for parallel dev + isolated review diffs.
Prefer basing truly-independent lanes on `main` (not the spine) from the start so
only the shared-file conflict remains.

**Related gotcha — multi-issue auto-close:** a PR body with `Closes #a, #b, #c`
only auto-closes the **first** issue (#a). Each issue needs its own keyword:
`Closes #a, Closes #b, Closes #c`. When one PR closes several (consolidated
lanes), either write the keyword per issue or `gh issue close` the rest manually
after merge. See [[project_fow_totex_lcoe_economics_epic]],
[[feedback_recover_stale_branch_for_pr]], [[reference_force_push_denied_history_blob_remediation]].
