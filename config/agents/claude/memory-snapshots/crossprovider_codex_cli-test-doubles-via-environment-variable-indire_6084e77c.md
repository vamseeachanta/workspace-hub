---
name: crossprovider codex cli-test-doubles-via-environment-variable-indire
description: CLI test doubles via environment variable indirection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell-scripting, testing, dependency-injection]
---

For shell scripts that invoke external CLIs, use env var overrides with defaults (e.g., `CLAUDE_CMD="${CLAUDE_CMD:-claude}"`) instead of hardcoding command names. This enables test injection and mocking without modifying the script itself.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
