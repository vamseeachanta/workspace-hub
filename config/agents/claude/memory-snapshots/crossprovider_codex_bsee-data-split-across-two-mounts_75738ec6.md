---
name: crossprovider codex bsee-data-split-across-two-mounts
description: BSEE data split across two mounts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-24
  tags: [data-architecture, bsee, filesystem-layout]
---

BSEE .bin tables live at `/mnt/ace/worldenergydata/data/modules/bsee/bin/`; loader code and schemas live at `/mnt/local-analysis/worldenergydata/`. The relocation log documents this split. Both locations are required for full dataset access and schema navigation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
