---
name: crossprovider gemini multi-phase-migrations-require-explicit-verifica
description: Multi-phase migrations require explicit verification gates
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [operations, migration, verification]
---

Safe migrations (specs, configs, large refactors) need: (1) dry-run logging, (2) source checksums via sha256sum, (3) file count parity before/after, (4) target path verification, (5) pointer README validation. Use the logs and checksums as approval artifacts before apply phase.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
