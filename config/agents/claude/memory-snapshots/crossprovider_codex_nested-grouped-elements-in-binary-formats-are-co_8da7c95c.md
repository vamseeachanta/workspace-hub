---
name: crossprovider codex nested-grouped-elements-in-binary-formats-are-co
description: Nested/grouped elements in binary formats are commonly missed by standard libraries
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [binary-formats, pptx, nested-elements, edge-cases]
---

PPTX shapes inside groups (p:grpSp//p:pic), SVG elements nested in g tags, etc. are often not traversed by standard shape/object iterators. python-pptx.shapes walks only top-level; grouped pictures are children of the group shape. Raw XML parsing or explicit recursion is needed for complete coverage. This is a common gap in enrichment/extraction tools.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
