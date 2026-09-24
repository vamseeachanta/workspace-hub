---
name: crossprovider codex file-verification-must-use-canonical-source-git-
description: File verification must use canonical source (git show HEAD, not working tree); ls after Write
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, verification, caching, file-modes, tools-reliability]
---

After a Write operation, the working tree may be cached. After a commit, verify via `git show HEAD:<path>`, not the filesystem. After `chmod +x` or mode changes with `git update-index --chmod`, verify with `git ls-tree HEAD`, not `git ls-files -s`. A change invisible to the canonical source did not land.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
