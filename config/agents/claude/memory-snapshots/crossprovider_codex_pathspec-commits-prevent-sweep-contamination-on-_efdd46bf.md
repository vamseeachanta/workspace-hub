---
name: crossprovider codex pathspec-commits-prevent-sweep-contamination-on-
description: Pathspec commits prevent sweep contamination on shared NTFS-FUSE mounts
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [git, shared-infrastructure, automation-hazard]
---

Use `git commit -m "..." -- <paths>` form when multiple independent changes are staged. On shared mounts with auto-sync, the 4-hourly sync commits the dirty tree onto checked-out branch; broad `git add .` followed by auto-sync can sweep unrelated files into a PR.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
