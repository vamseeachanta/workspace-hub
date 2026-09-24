---
name: crossprovider codex schema-validators-require-injectable-contract-ap
description: Schema validators require injectable contract APIs, not hardcoded tuples
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing-API, contract-pattern, validator-extensibility]
---

When implementation will load a contract or manifest (e.g., #62 handoff fields), tests must be able to inject alternative contracts. Hardcoded production values are fine for defaults, but lack of test-injection prevents contract-aware testing and forces brittle phrase-matching.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
