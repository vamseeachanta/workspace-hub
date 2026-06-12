---
name: crossprovider hermes worktree-smoke-tests-validate-mechanics-only-not
description: Worktree smoke tests validate mechanics only, not topology
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, worktree, validation-scope]
---

Feature-branch worktree validation (e.g., ecosystem-sync wrapper/logging) succeeds locally but doesn't exercise production topology (git pull behavior, multi-machine state). Always require live-checkout validation on main for topology-dependent features.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
