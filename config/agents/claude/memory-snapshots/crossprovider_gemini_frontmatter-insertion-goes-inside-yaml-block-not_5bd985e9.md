---
name: crossprovider gemini frontmatter-insertion-goes-inside-yaml-block-not
description: Frontmatter insertion goes inside YAML block, not after
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [yaml, frontmatter, editing]
---

When parent feature WRK has no `children:` key, insert it BEFORE the closing `---` (inside frontmatter), not appended after the document. Use Python heredoc pattern: re.sub between header and closing delimiter.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
