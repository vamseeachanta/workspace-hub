---
name: crossprovider codex nested-worktree-registry-resolution-limitations
description: Nested worktree registry resolution limitations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-worktrees, registry-resolution, nested-paths]
---

Nested worktrees may fail to resolve sibling repositories via default resolvers; null hashes convert to misleading drift-detection results. Explicitly configure base registry paths and verify all expected repositories resolve before trusting change detection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
