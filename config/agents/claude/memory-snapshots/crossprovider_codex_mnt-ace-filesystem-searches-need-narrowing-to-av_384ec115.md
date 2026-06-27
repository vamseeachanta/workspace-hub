---
name: crossprovider codex mnt-ace-filesystem-searches-need-narrowing-to-av
description: /mnt/ace filesystem searches need narrowing to avoid noise
metadata:
  type: reference
  source: codex
  bridged: 2026-06-26
  tags: [filesystem-search, dev-workflow, coordination]
---

Broad filename searches across `/mnt/ace` generate excessive output due to large well and engineering datasets. Narrow to extension filters, specific subdirectories, and timeouts; coordinate parallel explorers to avoid collisions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
