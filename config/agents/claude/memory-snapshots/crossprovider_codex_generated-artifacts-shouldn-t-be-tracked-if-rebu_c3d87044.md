---
name: crossprovider codex generated-artifacts-shouldn-t-be-tracked-if-rebu
description: Generated artifacts shouldn't be tracked if rebuilt by hooks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [generated-artifacts, hooks, worktree-churn, cache-strategy]
---

A tracked generated file (e.g., symbol index, API manifest) that's rebuilt by post-merge hooks will cause worktree churn after pulls. Either treat it as untracked cache, explicitly ignore the output, or remove the automatic rebuild.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
