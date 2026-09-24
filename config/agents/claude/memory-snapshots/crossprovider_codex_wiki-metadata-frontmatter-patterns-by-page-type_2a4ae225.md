---
name: crossprovider codex wiki-metadata-frontmatter-patterns-by-page-type
description: Wiki metadata frontmatter patterns by page type
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [wiki-conventions, metadata-patterns, public-safety]
---

Concept pages require title, tags, sources, added, last_updated. Rich source pages add code_id, publisher, revision, jurisdiction, license_status, parse_status. Tooling consumes only a subset; graph generation explicitly skips absolute paths like /mnt/ace to prevent private-path leakage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
