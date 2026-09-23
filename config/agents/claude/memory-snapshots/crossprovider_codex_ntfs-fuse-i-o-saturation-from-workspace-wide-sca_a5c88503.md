---
name: crossprovider codex ntfs-fuse-i-o-saturation-from-workspace-wide-sca
description: NTFS-FUSE I/O saturation from workspace-wide scans
metadata:
  type: reference
  source: codex
  bridged: 2026-07-21
  tags: [ntfs-fuse, io-discipline, workspace-health, parallel-audits]
---

Broad recursive scans (`find`, `rg`) against `/mnt/local-analysis` saturate the NTFS-FUSE mount and hang `git` operations. The problem extends beyond git: parallel audit processes themselves can contribute to saturation. Require bounded scans with pruning/timeouts and add I/O-pressure preflights before launching parallel audits. Interrupted agents may leave child scanner processes running, perpetuating I/O pressure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
