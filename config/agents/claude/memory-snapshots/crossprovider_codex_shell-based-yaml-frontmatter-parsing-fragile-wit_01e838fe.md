---
name: crossprovider codex shell-based-yaml-frontmatter-parsing-fragile-wit
description: Shell-based YAML frontmatter parsing fragile without defensive normalization
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [shell-scripting, yaml-parsing, parsing-robustness]
---

Scope guard and similar tools that parse YAML frontmatter in bash are error-prone: spacing, CRLF, duplicate keys, comments, and malformed files trip regex-based extraction. Keep shell parsing minimal and defensive with bounded extraction, CRLF normalization, and fail-closed on ambiguous matches; prefer Python or a single reader/writer interface.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
