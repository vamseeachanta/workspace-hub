---
name: crossprovider gemini yaml-block-style-values-missed-by-line-based-reg
description: YAML block-style values missed by line-based regex extraction
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [yaml-parsing, frontmatter-extraction, schema-integration]
---

Simple regex `m = re.search(rf"^{field}:[ \t]*(.*)$", ...)` only captures values on the same line. Multi-line YAML blocks (e.g., `blocked_by:` with list items below) return empty string. Use proper YAML parsing or detect block indicators (`:` followed by newline) separately.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
