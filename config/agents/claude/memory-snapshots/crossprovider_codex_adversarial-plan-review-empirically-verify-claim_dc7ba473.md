---
name: crossprovider codex adversarial-plan-review-empirically-verify-claim
description: Adversarial plan review: empirically verify claims against actual configs, separate worktree measurements from source facts
metadata:
  type: reference
  source: codex
  bridged: 2026-08-14
  tags: [review-methodology, adversarial-review, measurement]
---

Plan text claims about gates/workflows must be verified against the actual source configs and run evidence, not taken as ground truth. When measuring behavior, use non-mutating techniques (config flags like `uv -o`, readonly collection flags) to avoid dirtying the worktree; separate worktree-dependent state from source-file facts in the evidence trail.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
