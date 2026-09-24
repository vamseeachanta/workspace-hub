---
name: crossprovider codex test-execution-fails-silently-in-read-only-sandb
description: Test execution fails silently in read-only sandboxes without writable temp
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing-constraint, sandbox]
---

pytest, uv, and build tools require writable /tmp or equivalent. Read-only sandboxes fail silently; verify writable temp availability and rerun before claiming test results valid in constrained environments.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
