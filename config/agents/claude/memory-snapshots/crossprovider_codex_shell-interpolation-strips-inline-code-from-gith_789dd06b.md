---
name: crossprovider codex shell-interpolation-strips-inline-code-from-gith
description: Shell interpolation strips inline code from GitHub API payloads
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [github-api, shell-scripting, content-preservation]
---

GitHub issue bodies crafted via shell variables and echo lose inline code formatting when interpolation occurs. Literal-file (HEREDOC) approach preserves code blocks; required when body contains markdown code spans or escaped special characters.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
