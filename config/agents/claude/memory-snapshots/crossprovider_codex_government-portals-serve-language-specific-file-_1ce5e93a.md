---
name: crossprovider codex government-portals-serve-language-specific-file-
description: Government portals serve language-specific file variants with different schemas
metadata:
  type: reference
  source: codex
  bridged: 2026-07-05
  tags: [data-engineering, localization, parser-robustness]
---

A statistics portal with language toggles (EN/ES) may point to different XLSX files with different column headers, ordering, or even sheet names. The parser must specify which language version it expects and provide the exact download URL (not a generic 'statistics' link). Spanish CORES workbooks have different headers than English CORES workbooks from the same portal.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
