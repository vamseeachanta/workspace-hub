---
name: crossprovider codex private-paths-in-tracked-artifacts-leak-topology
description: Private paths in tracked artifacts leak topology even without child listings
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-privacy, artifact-hygiene, public-repo]
---

Raw private/client path names in committed HTML/JSON reports are a leakage channel when a repo is public, even if child paths are omitted. Use redacted stable IDs (e.g., quarantine_root_001) in tracked artifacts; keep raw private path mappings out of git or in untracked operator logs only.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
