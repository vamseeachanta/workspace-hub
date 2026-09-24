---
name: crossprovider gemini spec-migration-script-contract-requires-fail-fas
description: Spec migration script contract requires fail-fast and idempotent apply
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [migration, spec-migration, workflow-pattern]
---

Migration scripts must fail if target files pre-exist (not overwrite), produce fixed-format dry-run summaries, and guarantee that a second `--apply` on identical state is a no-op. Source-to-target path mapping and SHA-256 parity validation prevent silent data loss and enable automated verification.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
