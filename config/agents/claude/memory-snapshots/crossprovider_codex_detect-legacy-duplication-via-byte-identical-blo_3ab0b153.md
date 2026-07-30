---
name: crossprovider codex detect-legacy-duplication-via-byte-identical-blo
description: Detect legacy duplication via byte-identical blob checks
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [architecture, auditing, data-quality]
---

When a dataset or SQL bundle appears in multiple locations, check for byte-identity between seed files across repo paths (e.g., `Sastry/*.sql` vs `data_manager/db/*.sql`). Identical blobs indicate legacy copies rather than independent algorithm boundaries; confirm by checking for consumers, entry points, and test suites.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
