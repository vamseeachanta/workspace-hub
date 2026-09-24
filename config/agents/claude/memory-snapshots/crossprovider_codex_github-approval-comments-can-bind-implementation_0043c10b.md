---
name: crossprovider codex github-approval-comments-can-bind-implementation
description: GitHub approval comments can bind implementation to specific plan SHA
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow, approval-binding, revision-control]
---

When an approval comment specifies a plan commit SHA or revision, implementation must fetch that exact approved text from origin/remote, not rely on the local copy, which may be stale. This lock prevents implementation drift and ensures scope fidelity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
