---
name: crossprovider gemini shell-script-testability-via-command-name-enviro
description: Shell script testability via command name environment variables
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [shell-testing, command-injection, test-harness]
---

Externalizing CLI tool names via environment variables (e.g., `CLAUDE_CMD="${CLAUDE_CMD:-claude}"`) enables test injection of missing or non-existent commands without modifying script logic. Appears as a pattern in cross-provider review script hardening.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
