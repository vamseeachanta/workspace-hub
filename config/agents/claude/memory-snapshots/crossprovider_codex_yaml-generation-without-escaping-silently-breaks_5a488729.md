---
name: crossprovider codex yaml-generation-without-escaping-silently-breaks
description: YAML generation without escaping silently breaks frontmatter
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [yaml, frontmatter, escaping]
---

Interpolating user input directly into double-quoted YAML scalars produces invalid frontmatter when titles contain quotes or backslashes. Use `yaml.safe_dump()` or explicit escaping of `"` and `\` before emitting `title: "..."`. WRK-1130 had this regression.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
