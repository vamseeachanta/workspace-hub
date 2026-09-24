---
name: crossprovider codex cli-file-path-argument-boundaries
description: CLI file path argument boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, cli-safety, file-io]
---

Scripts accepting `--schema`, `--manifest`, `--report` paths must validate those paths remain within approved directories. Without boundary enforcement, arbitrary parent-directory writes and source-tree reads become possible even in otherwise sandboxed logic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
