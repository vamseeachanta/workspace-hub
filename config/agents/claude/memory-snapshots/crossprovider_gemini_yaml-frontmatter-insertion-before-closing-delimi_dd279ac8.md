---
name: crossprovider gemini yaml-frontmatter-insertion-before-closing-delimi
description: YAML frontmatter insertion: before closing delimiter, not after
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [yaml, python, frontmatter]
---

When a Python script inserts a new YAML key into frontmatter, insert BEFORE the closing `---` delimiter, not appended after the document body. Use re.sub with MULTILINE flag to update status fields in-place. Incorrect placement breaks YAML parsing.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
