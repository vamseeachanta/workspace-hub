---
name: crossprovider codex pytest-collection-root-cause-diagnosis-requires-
description: pytest collection root-cause diagnosis requires repo-by-repo isolation; no universal culprit
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pytest, collection, diagnostics, performance, ntfs-fuse]
---

Collection slowness >30s budget can stem from: (a) plugin entry-point discovery on NTFS-FUSE (digitalmodel >180s), (b) post-collection hooks with SQLite I/O (worldenergydata >100s), or (c) conftest real work (assetutilities fast despite async conftest). Single-file baseline (~1.5s process overhead) vs full-suite time does not correlate with cause. Bisect by disabling plugins, disabling conftest, measuring single file, then measuring 900s baseline to isolate class.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
