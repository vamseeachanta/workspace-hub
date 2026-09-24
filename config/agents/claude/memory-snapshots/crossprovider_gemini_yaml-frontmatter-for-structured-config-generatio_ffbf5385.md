---
name: crossprovider gemini yaml-frontmatter-for-structured-config-generatio
description: YAML frontmatter for structured config generation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [architecture, config-management]
---

When generating machine-readable config from human-editable files, embed data as YAML frontmatter (at the top of files like AGENTS.md) instead of parsing free-form text. Text parsing is fragile and breaks on minor formatting changes; frontmatter is explicit and reliable.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
