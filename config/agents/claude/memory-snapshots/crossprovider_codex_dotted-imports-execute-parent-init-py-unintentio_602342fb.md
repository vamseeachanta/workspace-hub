---
name: crossprovider codex dotted-imports-execute-parent-init-py-unintentio
description: Dotted imports execute parent __init__.py unintentionally
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [python, import, testing]
---

Moving from spec_from_file_location to normal imports now initializes every ancestor module's __init__.py. Any exception in a parent blocks all children. Old file-path loading bypassed this chain, so tests marked passing may actually fail under real import.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
