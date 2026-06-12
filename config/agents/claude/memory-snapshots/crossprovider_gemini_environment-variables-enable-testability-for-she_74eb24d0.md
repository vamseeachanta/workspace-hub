---
name: crossprovider gemini environment-variables-enable-testability-for-she
description: Environment variables enable testability for shell commands
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [testing, shell-design, orchestration]
---

Pattern: `COMMAND_CMD="${COMMAND_CMD:-default}"` allows tests to inject non-existent command names to verify fallback/error paths without mocking. Applied to claude/codex/gemini submit scripts.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
