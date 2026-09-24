---
name: crossprovider codex hub-root-configs-require-explicit-dispatch-from-
description: Hub-root configs require explicit dispatch from per-repo hooks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [config-discovery, hooks, multi-repo, tool-integration]
---

Shared configs at workspace root are not automatically found by per-repo hook invocations. Per-repo hooks must use explicit `--config` paths or config shims in each repo. Relying on implicit discovery leaves per-repo hooks unaware of hub-level settings.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
