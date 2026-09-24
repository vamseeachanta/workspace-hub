---
name: crossprovider codex filesystem-searches-need-scoping-before-enumerat
description: Filesystem searches need scoping before enumeration
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [filesystem, performance, scoping, large-datasets]
---

Broad `find` calls across large mounts (e.g., `/mnt/ace` with 60+ root entries) are slow and noisy. Use extension filters (`.bin`, `.json`), known subdirectory scoping (e.g., `worldenergydata/data/modules`), and structure-aware probes first; enumerate only high-probability candidates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
