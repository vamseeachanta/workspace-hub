---
name: crossprovider codex privacy-first-classification-for-data-inventory-
description: Privacy-first classification for data inventory in shared workspaces
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [data-governance, privacy, inventory, security]
---

When inventorying multi-repo data roots, classify each root as public/private/unknown BEFORE any listing/inspection. Default unknown roots to quarantine. Pattern-match sensitive names (client_*, mkt-a-*, *-projects) for automatic quarantine. Include symlink resolution in quarantine logic—symlink chains can hide sensitive data from classification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
