---
name: crossprovider codex wave-based-migrations-with-checksum-validation-p
description: Wave-based migrations with checksum validation prevent silent corruption
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [migrations, data-integrity, operational]
---

Migrations >1K files should use wave-based rollout (small pilot, then larger corpus). Each wave: dry-run with source/target checksum capture, apply with dedicated commit, scope-guard commit diff, continuity check before next wave. Checksums must be normalized for path comparison.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
