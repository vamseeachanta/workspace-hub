---
name: crossprovider codex file-extension-matching-must-be-case-insensitive
description: File extension matching must be case-insensitive in security classifiers
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [security, testing, cross-platform]
---

Uppercase extensions (`.EXE`, `.DLL`, `.INF`) are distinct from lowercase on case-sensitive filesystems. Security-critical file-type checks must use case-insensitive matching and include tests for both cases.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
