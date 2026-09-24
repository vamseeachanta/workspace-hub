---
name: crossprovider codex windows-collector-support-must-have-fixture-test
description: Windows collector support must have fixture tests, not assumptions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [windows-compatibility, os-branch, test-fixtures]
---

OS-support claims need fixture tests for Linux/macOS/Windows variants; wmic is unreliable on modern Windows; Git Bash uname values (MINGW*, MSYS*) need explicit branching, not best-effort fallback.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
