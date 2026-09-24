---
name: crossprovider codex metadata-fabrication-breaks-audit-trails-in-expo
description: Metadata Fabrication Breaks Audit Trails in Export/Capture
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [provenance, audit-trails, export-design]
---

Hardcoded/placeholder metadata in export records (fixed `captured_at`, `content_type=text/csv` for all exports) defeats traceability when real provenance differs. Preserve actual timestamps, content types, and source URLs in export metadata; placeholders make it impossible to audit what was actually exported and when.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
