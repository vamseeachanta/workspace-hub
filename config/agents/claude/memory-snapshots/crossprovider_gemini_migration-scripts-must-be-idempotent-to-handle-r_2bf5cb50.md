---
name: crossprovider gemini migration-scripts-must-be-idempotent-to-handle-r
description: Migration scripts must be idempotent to handle re-runs safely
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [idempotence, migration, robustness]
---

Rerunning migrate/scaffold scripts should not duplicate files or corrupt stage folders. Use 'already exists, skipping' patterns rather than erroring on collisions.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
