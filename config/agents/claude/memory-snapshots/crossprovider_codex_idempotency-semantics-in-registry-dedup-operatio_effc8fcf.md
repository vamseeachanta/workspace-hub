---
name: crossprovider codex idempotency-semantics-in-registry-dedup-operatio
description: Idempotency semantics in registry/dedup operations must be explicitly defined
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [api-design, registry, idempotency]
---

Registry code with documented idempotency had inconsistent implementation: docstring specified exact-match uniqueness, but code deduplicates entries within tolerance, potentially merging distinct records. Idempotent operations need a precise uniqueness criterion defined in both documentation and implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
