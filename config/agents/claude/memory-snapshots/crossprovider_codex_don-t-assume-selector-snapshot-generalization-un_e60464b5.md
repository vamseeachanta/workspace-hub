---
name: crossprovider codex don-t-assume-selector-snapshot-generalization-un
description: Don't assume selector/snapshot generalization until implemented
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [dependencies, futures, scope-creep]
---

Sessions 1-2 found #52 and #63 plans assuming #72's generalized selector/snapshot modes were available, but #72 hadn't landed yet. Plans depending on future generalization must stay on explicit-path modes (e.g., --scan-public-path) until the upstream generalization is actually merged.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
