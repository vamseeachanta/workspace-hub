---
name: crossprovider codex case-folding-collision-detection-in-path-based-m
description: Case-folding collision detection in path-based migrations
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [path-migration, cross-platform, collision-detection]
---

When migrating paths across repos, detect not just exact duplicates but case-folding collisions (e.g., `Specs/README.md` vs `specs/README.md`). Critical on NTFS/macOS filesystems; easy to miss on Linux. WRK-188 added explicit case-folding checks alongside exact-match deduplication.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
