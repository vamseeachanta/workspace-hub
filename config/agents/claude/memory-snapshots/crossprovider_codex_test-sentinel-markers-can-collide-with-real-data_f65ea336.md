---
name: crossprovider codex test-sentinel-markers-can-collide-with-real-data
description: Test sentinel markers can collide with real data paths and corrupt merging
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, parser, sentinel-collision]
---

Using markers like `__codex_sync_probe__` in a path-truncation helper silently breaks if a real table path contains that string. The truncated path causes nested keys to be misclassified as owned. Use per-line sentinels or path-restricted whole-file exemptions, not blanket truncation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
