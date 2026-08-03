---
name: crossprovider codex name-based-guards-break-on-file-rename
description: Name-based guards break on file rename
metadata:
  type: reference
  source: codex
  bridged: 2026-08-02
  tags: [harness, guards, infrastructure]
---

Harness guards that enumerate filenames by hardcoded name fail when files are renamed (e.g., CLAUDE.md → config/agents/claude/SOUL.runtime.md). Use role-based registry or derivation from a canonical source (e.g., build-soul-runtime.sh's output list), not enumeration. Repeat of issue #3744.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
