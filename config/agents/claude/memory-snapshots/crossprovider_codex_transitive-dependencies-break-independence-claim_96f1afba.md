---
name: crossprovider codex transitive-dependencies-break-independence-claim
description: Transitive dependencies break independence claims
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dependency-analysis, tool-independence, verification]
---

When two tools appear independent (different codebases, different languages), shared transitive dependencies (e.g., olefile for CFB parsing) still create a common failure mode. Independence claims require checking transitive dependency overlap, not just direct imports.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
