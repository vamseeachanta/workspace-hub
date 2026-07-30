---
name: crossprovider codex preserve-untracked-user-files-in-dirty-private-r
description: Preserve untracked user files in dirty private-repo checkouts
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [private-repos, fuse-i-o, git-discipline, ntfs]
---

When a private-repo checkout has untracked files (e.g., pre-existing notes), preserve them rather than force-merging or cleaning. Slow FUSE I/O can spawn orphaned git processes from probes; terminate only known probe/merge processes, not entire sessions. Use lower-I/O update paths (e.g., bounded partial clone) to avoid livelock.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
