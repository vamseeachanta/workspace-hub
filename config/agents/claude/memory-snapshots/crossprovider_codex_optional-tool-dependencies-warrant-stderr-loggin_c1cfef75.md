---
name: crossprovider codex optional-tool-dependencies-warrant-stderr-loggin
description: Optional tool dependencies warrant stderr logging
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, diagnostics, error-handling]
---

When a tool like `jq` is optional or may be missing, emit a warning to stderr rather than silently ignoring failures. Silent failures make debugging harder and hide data loss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
