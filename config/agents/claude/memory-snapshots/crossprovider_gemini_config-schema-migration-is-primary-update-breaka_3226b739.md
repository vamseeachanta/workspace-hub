---
name: crossprovider gemini config-schema-migration-is-primary-update-breaka
description: Config schema migration is primary update breakage vector
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [deployment, tool-updates, configuration-management]
---

Configuration file schema changes during tool version bumps are a leading cause of breakage and should be validated as part of update procedures, not treated separately from binary/script updates.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
