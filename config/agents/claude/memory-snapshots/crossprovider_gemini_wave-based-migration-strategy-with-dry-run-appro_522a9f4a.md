---
name: crossprovider gemini wave-based-migration-strategy-with-dry-run-appro
description: Wave-based migration strategy with dry-run → approval → apply → verification
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [migration, data-integrity, governance]
---

Data migrations (specs, configs, large file trees) use bounded waves, never monolithic. Each wave: dry-run captures manifest + checksums, gets approval, applies with rollback capability, runs idempotency check. Second apply on clean state must produce zero diff.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
