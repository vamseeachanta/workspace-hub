---
name: crossprovider codex case-folding-collision-detection-in-multi-repo-m
description: Case-folding collision detection in multi-repo migrations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [migrations, path-collisions, cross-platform, preflight]
---

When migrating paths across repos or filesystems with mixed case-sensitivity, check both exact-match and case-folded duplicates (e.g., path/specs vs path/SPECS). A second path differing only in case silently collides on case-insensitive filesystems (Windows, macOS), causing data loss or corruption.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
