---
name: crossprovider codex privacy-in-auto-generated-artifacts
description: Privacy in auto-generated artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [privacy, memory-artifacts, session-state]
---

Untracked memory files, session artifacts, and research notes from Claude/Codex sessions contain private operational context that shouldn't sweep into sync commits. Require explicit owner review before including them; use pathspec commits and stash to avoid blind inclusion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
