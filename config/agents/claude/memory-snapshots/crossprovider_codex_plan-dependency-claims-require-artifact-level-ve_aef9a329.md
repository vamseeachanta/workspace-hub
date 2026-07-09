---
name: crossprovider codex plan-dependency-claims-require-artifact-level-ve
description: Plan dependency claims require artifact-level verification
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [planning, dependencies, validation, verification]
---

When a plan claims to "consume" or depend on another contract/artifact, verify it's actually loaded or imported in pseudocode and tests, not just named in prose. Validate against current implementation status of dependencies (already-implemented vs. future); don't trust prose without code evidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
