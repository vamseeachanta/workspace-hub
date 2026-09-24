---
name: crossprovider codex sandbox-test-failures-from-read-only-caches-are-
description: Sandbox test failures from read-only caches are benign
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, sandbox, python, debugging]
---

UV and other tools fail to compile or run in sandboxed environments when cache directories (e.g., ~/.cache/uv) are read-only, but pass outside sandbox with identical code. Distinguish sandbox noise from real defects by rerunning outside sandbox before assigning severity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
