> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-18
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_parallel_branch_checkout_working_dir.md

---
name: parallel-branch-checkout-working-dir
description: "When a parallel session checks out a feature branch in the same git tree, your working directory's file contents become that branch's state — even if main has your commits. Verify with git reflog/branch, not file contents on disk."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 37c4fd1d-3784-4903-a5ea-5fe997dd7044
---

**A file on disk doesn't tell you which branch you're on. Always check `git branch --show-current` AND `git reflog` before reacting to "missing" changes.**

**Why:** 2026-05-13 — During parallel work in digitalmodel, the catenary canonicalization Phase 2 (`__init__.py` migration + base file deletion) committed to `main` as `cec18733`. A parallel session then ran `git checkout` to a feature branch (`issue-594-vessel-operability-plan`) starting from a commit BEFORE Phase 2. The working directory's files reverted to that branch's state. The system flagged the `__init__.py` modification as "intentional" — true *for the parallel session's branch*, but misleading for me.

**How to apply:**

1. When a system-reminder says a file you edited "was modified" — don't assume your work was lost. First check:
   ```bash
   git branch --show-current     # are we on main or a sibling branch?
   git rev-parse main            # is main where I left it?
   git merge-base --is-ancestor <my-commit-sha> main && echo "preserved"
   git reflog | head -20         # what sequence of events happened?
   ```
2. If the commit is on main but the working directory is on a feature branch, that's a parallel-session checkout — NOT a reset/revert. Your work is safe.
3. If the commit is gone from `git log --all`, check for dangling objects:
   ```bash
   git cat-file -t <my-sha>      # 'commit' = still exists as dangling object
   git fsck --lost-found
   ```
4. Per `feedback_reflog_as_ground_truth`: reflog is the authoritative record of *what HEAD did*, not what files look like.
5. Per `feedback_check_parallel_work`: scan for parallel sessions before assuming malice; another session checking out a different branch is the most common explanation.

**Do NOT:**
- Re-apply your "missing" work without checking reflog first — you may double-commit
- Force-checkout main while another session is using the working directory — disturbs their state
- Trust file mtimes — they reflect the most recent checkout, not your commit
