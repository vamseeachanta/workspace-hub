---
name: crossprovider codex inventory-shared-mounts-via-manifest-not-find-du
description: Inventory shared mounts via manifest, not find/du
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [inventory, shared-storage, manifest, performance]
---

Use pre-built JSON manifests (e.g., assets.json) instead of unbounded filesystem scans to inventory large shared mounts. Filesystem operations on large shares incur mounting pressure; manifests capture inventory state without live scanning.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
