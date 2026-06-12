---
name: crossprovider codex yaml-parser-fails-silently-on-unquoted-special-c
description: YAML parser fails silently on unquoted special chars in skill frontmatter
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [yaml-parsing, skill-loading, configuration]
---

Skill SKILL.md descriptions containing colons must be quoted; unquoted colons cause YAML parsing errors and the loader silently skips the malformed skill without warning the user. This leads to mysterious missing-command errors downstream.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
