---
name: crossprovider gemini large-migration-pattern-dry-run-gate-before-appl
description: Large migration pattern: dry-run gate before apply
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [migrations, governance, verification]
---

File migrations require: dry-run log review, source-target checksum parity, collision preflight, idempotence check (second apply produces no diff). Apply without gates creates unrecoverable state.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
