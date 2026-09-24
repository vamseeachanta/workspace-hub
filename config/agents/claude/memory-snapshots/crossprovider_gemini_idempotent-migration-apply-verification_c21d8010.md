---
name: crossprovider gemini idempotent-migration-apply-verification
description: Idempotent migration apply verification
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [idempotent-design, verification-strategy, spec-migration]
---

Spec migration scripts must verify idempotency—running `--apply` twice on clean post-migration state produces zero content diff. Use path-normalized checksum comparison (sed to strip migration paths, then diff) as the verification method.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
