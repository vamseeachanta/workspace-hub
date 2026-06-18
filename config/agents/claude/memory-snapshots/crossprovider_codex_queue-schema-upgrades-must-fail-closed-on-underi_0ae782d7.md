---
name: crossprovider codex queue-schema-upgrades-must-fail-closed-on-underi
description: Queue schema upgrades must fail-closed on underivable identity
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [data-safety, schema-migration, plan-review]
---

When rewriting queue rows with schema changes that derive identity from row data (e.g., table_id from csv_path), distinguish between 'skip with report' and 'abort with original unchanged'. Silently skipping rows during a full rewrite can be misread as data loss. Plans must specify fail-closed abort on any underivable row and acceptance tests that verify no upgraded row with empty identity exists.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
