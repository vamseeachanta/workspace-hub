> Git-tracked snapshot from Claude auto-memory. Captured: 2026-06-25
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_adversarial_review_before_user_approval.md

---
name: feedback-adversarial-review-before-user-approval
description: Never bring work to user review/approval (or merge) until adversarial review has run and left evidence; self-review during build does NOT satisfy the gate
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 08e3d2f3-8ca3-49c2-bc9d-390a767f25fa
---

**Sequence work to the user for approval/merge ONLY AFTER adversarial review has
run and produced evidence — at BOTH the plan stage and the code stage.** Do not
present a plan for `status:plan-approved`, and do not present a PR for merge,
until an adversarial (defect-hunting) review exists.

**Why:** on 2026-05-25 the #2795/#2796 dispatch work shipped through *both* user
gates (plan-approved, then merge) with **zero adversarial review** — PR had
`reviews=0`, no `scripts/review/results/` artifact, only my own status comments.
It went: interactive design → user plan-approved → build → user merged. My own
mid-build self-corrections (machine-vocab collision, domain-authority clobber,
rate-limit/false-drift bug) were real but are **self-review by the author**,
which the gate explicitly distinguishes from adversarial review by another
provider instructed to assume I'm wrong. A green pre-push "review-gate PASS"
masked the gap (it keys off commit metadata, not a real review artifact).

**How to apply:** the gate order is load-bearing, not optional —
Plan → **adversarial review** → `status:plan-review` → USER APPROVES →
implement → **adversarial review (code/artifact)** → USER MERGES. Before asking
the user to approve or merge, confirm review evidence exists; if a session is
permission-gated from dispatching cross-review, run a structured single-author
r-review with transparent provenance rather than skipping
([[feedback_permission_gate_blocks_cross_review]]). Scale depth T1/T2/T3 by scope
([[feedback_always_adversarial_review_scale_depth]], [[feedback_adversarial_review_stance]]).
Systemic/cross-repo work (this case: 1,485 issues across 12 repos) is T2–T3.
