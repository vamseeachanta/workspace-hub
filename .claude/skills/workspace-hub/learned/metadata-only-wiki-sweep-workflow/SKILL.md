---
name: metadata-only-wiki-sweep-workflow
description: Disciplined inventory process for cataloging documents by filename/path without content claims, using parent-centric grouping to prevent stub proliferation
version: 1.0.0
source: auto-extracted
extracted: 2026-04-13
metadata:
  tags: ["documentation", "wiki-management", "metadata-extraction", "inventory-process"]
---

# Metadata-Only Wiki Sweep Workflow

Use this when creating stub documentation for large document collections without making content claims. (1) Verify plan approval before execution. (2) Inventory all target directories and extract PDF metadata using `pdfinfo` for safe header-only reading. (3) Apply parent-centric grouping: merge fragment documents (page scans, figures, sections) into parent document entries rather than creating proliferating stubs. (4) Generate stubs with explicit "do not claim" sections listing what content verification hasn't occurred. (5) Validate stubs with regex checks for prohibited claim language ("normative", "shall", "must", "requires that") in actual content areas, excluding constraint headers.