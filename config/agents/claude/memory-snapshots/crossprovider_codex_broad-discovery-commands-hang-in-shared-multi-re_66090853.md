---
name: crossprovider codex broad-discovery-commands-hang-in-shared-multi-re
description: Broad discovery commands hang in shared multi-repo workspaces; narrow patterns early
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [performance, shell-patterns, discovery, workspace]
---

Full-repo grep/git-status queries hang or run slowly in workspaces with multiple large repos and corpus data. Use targeted patterns like `rg --files` or explicit file lists; avoid depending on full `git status` unless necessary.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
