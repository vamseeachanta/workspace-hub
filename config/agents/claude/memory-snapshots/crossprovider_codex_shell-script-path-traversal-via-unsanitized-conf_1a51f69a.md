---
name: crossprovider codex shell-script-path-traversal-via-unsanitized-conf
description: Shell script path traversal via unsanitized config sourcing
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [shell-security, path-traversal, input-validation]
---

Constructing `source "${repo}.conf"` from user input allows crafted values like `../../tmp/x` to source unexpected files if present. Whitelist allowed repo names or use absolute paths with validation before sourcing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
