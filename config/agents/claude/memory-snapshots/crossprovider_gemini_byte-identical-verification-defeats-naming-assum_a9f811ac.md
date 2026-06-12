---
name: crossprovider gemini byte-identical-verification-defeats-naming-assum
description: Byte-identical verification defeats naming assumptions
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [deduplication, content-verification, skills-audit]
---

Two skills with matching frontmatter `name` may have divergent file content (verified: 1 of 7 'duplicate' pairs actually identical). Assume names mislead; verify actual sha256 on artifacts before deletion. Divergent duplicates require diff/merge, not simple removal.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
