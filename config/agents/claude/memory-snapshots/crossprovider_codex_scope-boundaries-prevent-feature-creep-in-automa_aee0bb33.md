---
name: crossprovider codex scope-boundaries-prevent-feature-creep-in-automa
description: Scope boundaries prevent feature creep in automation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scope, automation, issue-boundaries, approval]
---

Original issue #3472 requested user-cache cleanup only; later plan iterations expanded to worktree deletion, OS package removal, privileged root operations. Each scope expansion is a separate decision requiring explicit approval. Gate feature additions at issue review, not in implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
