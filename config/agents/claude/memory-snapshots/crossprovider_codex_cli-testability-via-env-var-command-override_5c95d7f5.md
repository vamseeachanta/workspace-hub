---
name: crossprovider codex cli-testability-via-env-var-command-override
description: CLI testability via env-var command override
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testability, environment-variables, cli-patterns]
---

Injecting CLI commands through env vars (CLAUDE_CMD, CODEX_CMD, GEMINI_CMD with defaults) allows tests to verify fallback behavior without requiring all tools installed; patterns: `${CMD}_CMD:=command` with quoted variable expansion in exec calls.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
