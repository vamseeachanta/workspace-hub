---
name: crossprovider codex metadata-manifest-contracts-must-match-runtime-v
description: Metadata/manifest contracts must match runtime values
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [metadata, output-contract, defect]
---

Published metadata (manifest.json, selection_policy, quality counts) can become disconnected from actual CLI parameters or source data. Hard-coded defaults in metadata that don't reflect CLI arguments or dynamic selection criteria create misleading evidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
