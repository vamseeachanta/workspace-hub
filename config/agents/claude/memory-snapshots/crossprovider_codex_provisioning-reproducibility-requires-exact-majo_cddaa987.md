---
name: crossprovider codex provisioning-reproducibility-requires-exact-majo
description: Provisioning reproducibility requires exact major+build versions, not just package names
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [provisioning, reproducibility, benchmarking]
---

Benchmarking across machines needs identical OpenFOAM v2312 build 2312.260127-2 to ensure reproducible results; apt default may pin only major version. Re-provisioning must be idempotent (same run = same binary), with build artifacts versioned and validated post-install. Version mismatches create false performance claims.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
