---
name: crossprovider codex private-data-invalidates-reproducibility-assumpt
description: Private data invalidates reproducibility assumption
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, governance, reproducibility]
---

When generated artifacts depend on private/off-repo data (e.g., lane maps, raw-label rules), those artifacts cannot be deterministically regenerated from tracked sources alone. Declare this tension explicitly rather than claiming reproducibility when secret inputs are required.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
