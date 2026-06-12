---
name: crossprovider codex git-diff-binary-loses-new-files
description: `git diff --binary` loses new files
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [git, tool-quirk, ingest]
---

Patch capture via `git diff --binary` extracts only tracked modifications, not new files. For ingest workflows that create mostly new pages, commit directly in the worktree instead of patch-capture/apply. Session 2 identified this as BUG C — a critical loss of ingest output.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
