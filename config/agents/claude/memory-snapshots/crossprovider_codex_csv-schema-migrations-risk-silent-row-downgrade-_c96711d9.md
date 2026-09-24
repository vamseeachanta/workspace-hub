---
name: crossprovider codex csv-schema-migrations-risk-silent-row-downgrade-
description: CSV schema migrations risk silent row downgrade without validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-migration, csv-handling, schema-validation]
---

DictWriter using legacy headers silently omits columns not in the source header, causing newly appended rows to be incomplete. Migration code must validate incoming schemas and reject mismatches rather than accommodating legacy shapes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
