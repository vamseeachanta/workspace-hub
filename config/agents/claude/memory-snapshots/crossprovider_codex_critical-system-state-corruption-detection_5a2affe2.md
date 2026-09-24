---
name: crossprovider codex critical-system-state-corruption-detection
description: Critical system state corruption detection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [generated-output, data-integrity, blocker-detection]
---

Some generated resets indicate corruption, not normal refresh: skills catalogs collapsing from 40+ items to 0, baselines shrinking unexpectedly. Flag and block these before commit; they break downstream discovery/loading. Need explicit criteria per system (skills: must have >=1 entry; baselines: must match prior structure).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
