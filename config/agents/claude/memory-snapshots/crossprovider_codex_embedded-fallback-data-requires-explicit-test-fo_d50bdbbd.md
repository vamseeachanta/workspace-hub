---
name: crossprovider codex embedded-fallback-data-requires-explicit-test-fo
description: Embedded fallback data requires explicit test forcing or removal
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, fallback-patterns, production-safety]
---

Production adapters with embedded fallback data (hardcoded rows, stale defaults) stay untouched unless tests explicitly force or remove the fallback path. Normal-path testing leaves fallbacks unverified and stale.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
