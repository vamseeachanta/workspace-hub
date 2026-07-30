---
name: crossprovider codex catalog-extraction-quarantine-conflicts-instead-
description: Catalog extraction: quarantine conflicts instead of silent choice
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [data-integrity, catalog, extraction]
---

When extracting catalogs with duplicate/conflicting normalized keys, preserve every safe row with lineage and quarantine ambiguous entries. Never silently choose one and drop the rest. Expose only unambiguous canonical entries in the lookup API, maintaining data integrity and auditability.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
