---
name: crossprovider codex broad-scans-on-ntfs-mounts-saturate-i-o-without-
description: Broad scans on NTFS mounts saturate I/O without pruning
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [io-discipline, shared-mounts, performance]
---

Recursive scans (find, rg, git status) on shared NTFS mounts without timeouts or pruning saturate I/O (88–94% utilization, ~61% pressure) and hang concurrent git operations. Require bounded scans, preflight I/O pressure, and ensure interrupted agents terminate orphaned scanners.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
