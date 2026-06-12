---
name: crossprovider codex migration-rollback-requires-dedicated-apply-comm
description: Migration rollback requires dedicated apply commit and verified checksums
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [migrations, operational, recovery]
---

Rollback procedures must assume: (1) apply was a single, dedicated commit, (2) pre/post checksums are captured, (3) apply is aborted if mixed with unrelated changes. Without these constraints, rollback is unsafe and may lose data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
