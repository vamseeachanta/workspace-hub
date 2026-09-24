---
name: crossprovider codex shell-config-sourcing-requires-path-validation-t
description: Shell config sourcing requires path validation to prevent traversal
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell-security, path-traversal, input-validation]
---

When constructing file paths from user input for `source` or `. ` commands (e.g., `source config/${repo}.conf`), validate the repo name against an allowlist. Direct string interpolation without validation enables path-traversal attacks that can execute arbitrary local code.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
