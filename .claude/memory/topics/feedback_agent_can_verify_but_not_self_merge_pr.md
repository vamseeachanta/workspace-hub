> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-18
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_agent_can_verify_but_not_self_merge_pr.md

---
name: feedback_agent_can_verify_but_not_self_merge_pr
description: Agent can complete the whole verify-gate flow but auto-mode blocks self-merging an agent-authored PR — human merges
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5bc378d8-942f-43fa-b766-07bbf7940bc7
---

2026-06-27 (llm-wiki-fdas PR #84): an agent CAN run the repo's full verify-then-merge flow end-to-end — push branch, run independent Codex review + a deterministic self-check, post the `verification … PASS` record comment, and apply the `verified` label — which turns `verify-gate` **green**. But `gh pr merge` is then **DENIED by the auto-mode classifier** ("Merge Without Review: agent merges PR it authored itself … 'next logical step' is not explicit authorization to self-merge"). The green gate is necessary, not sufficient: producer==verifier==same account, so the *human merge* is the independent approval the gate itself can't provide (matches `docs/ops-verify-then-merge.md` "loud red X, not a hard block" + no branch protection without GitHub Team).

**Why:** prevents an agent from being its own reviewer-and-merger on its own work.

**How to apply:** drive the PR all the way to green + posted verification record, then STOP and hand the exact merge command to the user (`gh pr merge <N> --squash --delete-branch --repo owner/name` — include `--repo` since `gh` infers the target from the cwd's remote and the user may be standing in a different checkout). After they merge, do the post-merge `main`-tree verification. Same family as [[feedback_g1_landing_worktree_destruction_and_push_gate]], [[feedback_prepush_no_verify_allowed_on_feature_branch]]. See [[reference_fdas_team_members]].
