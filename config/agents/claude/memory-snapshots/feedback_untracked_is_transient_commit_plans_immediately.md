---
name: feedback_untracked_is_transient_commit_plans_immediately
description: "On workspace-hub, untracked files are DELETED by auto-sync — commit plans, approval markers and review evidence the moment they exist, not at the end"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 19c1569d-4a9e-4d87-bd34-50c2605be4d1
  modified: 2026-08-03T07:08:07.924Z
---

On `/mnt/local-analysis/workspace-hub`, **untracked means transient.** There is no state where a file quietly sits on disk.

2026-08-03: two plans and an approval marker were written, adversarially reviewed (r1 MAJOR ×2, r2 applied), formally approved by the owner — and then **vanished**. Every untracked file the session created was gone; everything tracked survived. The review artifacts under `scripts/review/results/` were still there. `docs/plans/*.md` and `.planning/plan-approved/3787.md` were not.

**Why:** the auto-sync job does not only *commit* the dirty tree onto whatever branch is checked out (the hazard in [[feedback_verify_the_branch_not_your_commits]]). It also *removes untracked files*. The mitigation adopted for the first hazard — return the checkout to `main` after pushing — protects committed work and leaves uncommitted work fully exposed.

Both directions were observed in one session: it deleted the untracked plans, then committed **and pushed** the same files to `main` within minutes of them being `git add`-ed.

**The sharpest case is the approval marker.** `.planning/plan-approved/<issue>.md` is what `scripts/enforcement/require-plan-approval.sh:68` READS to decide whether implementation may proceed. Its evidence was less durable than the work it gated. A dispatched agent had already refused to implement #3787 for want of that marker and was right; after the loss it would have refused again, for a reason unrelated to the work.

**How to apply:**
- **`git add` a plan, marker, or review artifact in the same turn you create it.** The standing "commit && push at every green milestone" rule is written for code; it applies at least as strongly to *gate evidence*, because that is what other agents read.
- Do not branch-and-PR docs on this repo reflexively — auto-sync pushes tracked files to `main` anyway. A `docs/`-only branch can end up empty relative to `main` before you open the PR. Check `git diff --name-only origin/main...HEAD` and `git cat-file -e origin/main:<path>` before assuming your branch carries anything.
- Anything genuinely scratch belongs in the session scratchpad, not in the repo working tree — the working tree is not a scratchpad here.
- Corollary for subagents: a report written only to `/tmp` survives; a plan written untracked into the repo may not. Brief them to commit deliverables.

Related: [[feedback_verify_the_branch_not_your_commits]], [[feedback_autorun_clobbers_subagent_worktree_commits]], [[feedback_autosync_silent_pusher]], [[feedback_never_offer_to_self_label_plan_approved]].
