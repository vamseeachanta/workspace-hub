---
name: crossprovider codex source-manifest-precedence-and-use-case-binding
description: Source manifest precedence and use-case binding
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-architecture, governance, source-of-truth, manifest-management]
---

When a codebase has multiple overlapping source manifests (e.g., broad file inventory vs domain-specific index), establish explicit per-use-case precedence rules and document which manifest is canonical for each downstream consumer. Avoid implicit or ambiguous precedence that leads to cache/sync inconsistencies.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
