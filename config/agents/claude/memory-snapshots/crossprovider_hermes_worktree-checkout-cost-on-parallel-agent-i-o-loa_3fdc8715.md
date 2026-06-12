---
name: crossprovider hermes worktree-checkout-cost-on-parallel-agent-i-o-loa
description: Worktree checkout cost on parallel-agent I/O load
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, performance, parallelism, large-repo]
---

Large repos (19K+ files) suffer 17–60+ min materialization when parallel agents contend for I/O. Reserve worktree isolation for final commit/push gates; run TDD iterations on live branch or isolated shallow clones.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
