---
name: crossprovider gemini duplicate-name-skills-may-have-divergent-content
description: Duplicate-name skills may have divergent content requiring merge before deletion
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [deduplication, merge-safety, audit]
---

Audit reports skill-name duplicates based on frontmatter collision detection, but actual file content often diverges. Example: 7 reported duplicates, only 1 byte-identical; others required manual diff/merge. Always verify content before deletion; do not assume duplicates are interchangeable.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
