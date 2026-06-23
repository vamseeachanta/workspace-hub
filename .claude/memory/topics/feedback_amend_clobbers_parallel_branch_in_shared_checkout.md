> Git-tracked snapshot from Claude auto-memory. Captured: 2026-06-23
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_amend_clobbers_parallel_branch_in_shared_checkout.md

---
name: feedback_amend_clobbers_parallel_branch_in_shared_checkout
description: "In the shared main checkout, git commit --amend can land on a parallel session's branch because they moved HEAD between your edit and commit — always use a dedicated worktree."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f7fadb7c-8e14-45c9-8014-2cbd970bbd6d
---

2026-06-14 (epic #3078 mission-spine, PR #3090): I authored `config/mission/mission-map.yaml` edits and committed in the SHARED main checkout `/mnt/local-analysis/workspace-hub`. Between my edits and my `git commit --amend`, a parallel session switched HEAD in that same checkout to its branch `fix/skills-curation-pyyaml` (commit 91fd0f42b, a 4-line pyyaml fix). My amend therefore landed on THEIR commit → produced a Frankenstein commit (ebd138304) carrying both their `skills-curation.sh` fix AND my mission-map under MY commit message, and left their branch pointing at it. Separately, another parallel session had already fast-forward-merged my seed branch to main and deleted my `epic-3078/mission-spine` ref. Net: my working file silently reverted to the seed and my branch vanished.

**Why:** the main checkout's HEAD/branch is shared mutable state across concurrent sessions. `--amend` (and any branch-relative commit) acts on whatever HEAD currently is — not what it was when you started editing. Parallel sessions move it without warning.

**How to apply:**
- For ANY commit/push work when parallel sessions may be active, work in a dedicated worktree: `git worktree add -b <branch> /tmp/wt-x origin/main`. Never edit+commit in the shared `/mnt/local-analysis/workspace-hub` checkout. The other sessions were already doing this (`/tmp/wt-*`); I wasn't.
- Recover commit objects via `git reflog` / `git cat-file -t <sha>` — amended/clobbered commits survive ~30 days. The correct file blob can be extracted with `git checkout <sha> -- <path>` (pulls ONE path, leaving contamination behind).
- If you clobber a parallel branch, repair it: `git branch -f <their-branch> <their-clean-sha>` (only when it's not checked out in any worktree — verify with `git worktree list`).
- Pre-push coverage gate breaks in a `/tmp` worktree (no sibling repos; `run-all-tests.sh --coverage` lib-path bug). `SKIP_COVERAGE_REASON="..."` is the hook's SANCTIONED bypass for code-free config pushes — distinct from the forbidden `SKIP_REVIEW_GATE`/`GIT_PRE_PUSH_SKIP` (see [[feedback_agent_cannot_enable_security_gate_bypass]]). The review gate must still pass.

Related: [[feedback_multi_agent_commit_serialization]] (pathspec commit to avoid sweep contamination), [[feedback_recover_stale_branch_for_pr]], [[feedback_reflog_as_ground_truth]], [[feedback_check_parallel_work]].
