---
name: crossprovider codex ci-safe-evidence-integrity-requires-content-hash
description: CI-safe evidence integrity requires content hashes, not references alone
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [evidence-integrity, ci-constraints, security]
---

Evidence registries that track artifacts by path/URL reference without content hashes enable tampering. Integrity-critical registries must include digest/hash fields that CI can re-compute and compare, especially when CI cannot query GitHub live for authorization verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
