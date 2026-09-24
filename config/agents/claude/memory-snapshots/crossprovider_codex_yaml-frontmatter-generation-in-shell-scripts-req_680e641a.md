---
name: crossprovider codex yaml-frontmatter-generation-in-shell-scripts-req
description: YAML frontmatter generation in shell scripts requires character escaping
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell-scripting, yaml, data-integrity]
---

When shell scripts emit YAML using heredocs or string interpolation, unescaped special characters in values (quotes, backslashes, newlines) produce invalid YAML. WRK-1130 discovered this when child titles containing `"` broke frontmatter parsing. Use a proper YAML library (Python `yaml.safe_dump`) or escape all special characters before interpolation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
