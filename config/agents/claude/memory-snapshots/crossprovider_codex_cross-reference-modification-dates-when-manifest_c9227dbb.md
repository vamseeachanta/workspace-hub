---
name: crossprovider codex cross-reference-modification-dates-when-manifest
description: Cross-reference modification dates when manifests are stale
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [staleness, inventory, data-freshness]
---

Central manifests may fall out of sync with subsystem updates. When auditing, check for supplementary indices with newer dates (e.g., `_cad-index/` vs. `assets.json`) and use the fresher source.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
