---
name: feedback_codex_exec_can_git_reset_your_commits
description: "A delegated codex exec session can run git reset and discard commits the delegating agent already made — reflog is the recovery path, and the delegator must verify its own commits survive"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3b006eae-10ef-4664-8b7a-316d95790cce
  modified: 2026-08-04T16:43:24.715Z
---

**A `codex exec` session dispatched into your worktree can run destructive git
operations on commits it did not create.**

2026-08-04, digitalmodel [#1576]: a lane authored slice-1 TDD (RED `04efcddf` →
GREEN `e5a70146`), then dispatched Codex for slice-2 tests. That Codex session
ran `git reset` and **discarded the GREEN commit**. The lane caught it via
`git reflog`, restored `e5a70146`, and authored slice 2 itself rather than
re-delegating. Verified after the fact: `git merge-base --is-ancestor e5a70146
<branch>` → present, so nothing was lost.

**Why:** the delegation model assumes Codex only adds work. It has full git
access in the worktree it is given, and nothing scopes it to "commits you
authored". A reset that looks locally reasonable to it — cleaning what it
believes is its own mess — silently destroys the delegator's history.

**How to apply:**

- **Record your HEAD SHA before dispatching Codex**, and verify it is still an
  ancestor afterwards: `git merge-base --is-ancestor <pre-dispatch-sha> HEAD`.
  Do this even when Codex reports success — it will not mention the reset.
- **`git reflog` is ground truth** for recovery. See
  [[feedback_reflog_as_ground_truth]]. Commit objects survive a reset until gc,
  so recovery is nearly always possible if you notice.
- **Push before delegating.** A pushed commit cannot be destroyed by a local
  reset, and the remote ref is an independent witness. This session pushed the
  #1633 branch after every Codex round for the analogous reason (a `/tmp`
  worktree holding the only copy of 8 commits).
- **Do not re-delegate the same slice after an incident.** The lane authored
  slice 2 itself, which was the right call — a second dispatch into a worktree
  whose state Codex has already misjudged compounds the risk.

Distinct from [[feedback_autorun_clobbers_subagent_worktree_commits]] (auto-sync
resetting worktree branches) and [[feedback_amend_clobbers_parallel_branch_in_shared_checkout]]
(`--amend` in a shared checkout). This one is the delegated tool itself.

See [[feedback_delegate_token_heavy_to_codex]] for when to delegate at all, and
[[feedback_subagent_write_phantom]] for the adjacent "verify, do not trust the
report" rule.
