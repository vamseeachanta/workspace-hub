---
name: crossprovider codex provider-skill-tree-canonical-architecture
description: Provider skill tree canonical architecture
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [multi-provider, symlinks, architecture]
---

Multi-provider agent setups (.claude, .codex, .gemini) use symlinks to a single canonical skill tree rather than duplicating trees per provider. This prevents divergence and duplication maintenance burden. Preserve symlink targets when refactoring audit systems.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
