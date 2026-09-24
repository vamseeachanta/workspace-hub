---
name: crossprovider codex four-tier-data-audit-classification-framework
description: Four-tier data audit classification framework
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-audit, evidence-levels, classification]
---

Classify data presence in four independent tiers: (1) filesystem-present, (2) drive-indexed, (3) metadata-processed, (4) actually-ingested. Each tier represents different evidence strength; presence at tier N does not prove tiers above it. Use lower-bound counts when timeouts occur.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
