---
name: crossprovider gemini content-hash-for-knowledge-object-identity
description: Content hash for knowledge object identity
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [identity, knowledge-management, design-pattern]
---

Use sha256(normalized_text) excluding frontmatter as stable identity for wiki pages and knowledge objects. This enables deduplication, caching, and change detection without creating self-reference loops.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
