---
name: crossprovider codex staged-vs-working-tree-config-binding-creates-to
description: Staged vs working-tree config binding creates TOCTOU in validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, staging, git, toctou]
---

Validation that reads configuration (e.g., taxonomy, domain allowlists) from the working tree during staged checks allows unstaged edits to authorize staged content absent from HEAD/index. Bind validation to Git index state (e.g., git cat-file blob HEAD:path) to close the window.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
