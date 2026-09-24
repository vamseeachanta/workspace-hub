---
name: crossprovider gemini archival-of-tracked-files-requires-git-aware-com
description: Archival of tracked files requires git-aware commands and dependency updates
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [archival, git, tracking]
---

Moving tracked files to `_archive/` requires (1) verifying git-tracked status first, (2) using `git mv` not `mv` to preserve history, (3) updating surviving files to remove hardcoded references or add forward-pointers per-skill (not per-family README).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
