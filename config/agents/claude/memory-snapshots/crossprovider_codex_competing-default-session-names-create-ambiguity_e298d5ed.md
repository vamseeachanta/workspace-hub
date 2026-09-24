---
name: crossprovider codex competing-default-session-names-create-ambiguity
description: Competing default session names create ambiguity
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [naming, defaults, configuration]
---

Multiple competing defaults for session names (work, main, `SESSION="${1:-work}"`) cause confusion and failed connects. Choose one canonical name, make it explicit in code and docs, and test the default path.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
