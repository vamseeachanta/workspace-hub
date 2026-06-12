---
name: crossprovider gemini yaml-frontmatter-in-markdown-files-embeds-struct
description: YAML frontmatter in Markdown files embeds structured data reliably
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [configuration, markdown, structured-data, pattern]
---

WRK-1073 approved using YAML frontmatter blocks in AGENTS.md for structured fields (entry_points, test_command, depends_on). Avoids separate config files and brittle Markdown parsing; machine-readable via standard YAML parsers. Pattern worth replicating.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
