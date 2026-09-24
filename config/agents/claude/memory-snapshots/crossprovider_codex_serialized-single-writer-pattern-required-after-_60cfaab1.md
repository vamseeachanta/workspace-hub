---
name: crossprovider codex serialized-single-writer-pattern-required-after-
description: Serialized single-writer pattern required after MAJOR parallel reviews
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [commit-safety, parallel-work, code-review]
---

When parallel reviews surface defects in shared files, use a single serialized writer to apply fixes; parallel patchers that target only initially reproduced examples leave bypasses and TOCTOU gaps. One writer ensures exhaustive fix coverage and transitive dependency handling.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
