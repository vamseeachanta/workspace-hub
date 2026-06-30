---
name: crossprovider codex worldenergydata-is-a-relocated-data-layer-not-a-
description: WorldEnergyData is a relocated data layer, not a git checkout
metadata:
  type: reference
  source: codex
  bridged: 2026-06-27
  tags: [worldenergydata, architecture, data-separation]
---

`/mnt/ace/worldenergydata` contains only `data/` and `docs/` directories; loader and processing code lives in the separate `/mnt/local-analysis/worldenergydata` git checkout. This separation avoids duplicating code on the large mount.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
