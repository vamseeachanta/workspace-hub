---
name: crossprovider gemini content-migration-to-work-within-file-size-const
description: Content migration to work within file size constraints
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [constraints, maintenance, file-management]
---

When hitting hard limits (e.g., CLAUDE.md 20-line constraint), migrate non-critical existing content to separate files before adding new mandatory content. Prevents circumventing constraints. WRK-658 v5.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
