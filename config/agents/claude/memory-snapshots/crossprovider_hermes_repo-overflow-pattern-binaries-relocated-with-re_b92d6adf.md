---
name: crossprovider hermes repo-overflow-pattern-binaries-relocated-with-re
description: Repo overflow pattern: binaries relocated with RELOCATION-LOG.md
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [repo-management, large-binaries, overflow-pattern]
---

Large repos (digitalmodel/, client-a/) keep working copies under /mnt/ace overflow dirs with RELOCATION-LOG.md documenting which files moved where and why. Prevents git bloat. References should use /mnt/ace/<repo>/docs/… paths, not git-tracked symlinks. When querying codebase, check both repo/.gitignore (git-tracked) and RELOCATION-LOG.md (overflow) for complete picture.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
