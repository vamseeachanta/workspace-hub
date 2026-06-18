---
name: crossprovider codex historical-data-migration-testing-must-check-one
description: Historical data migration testing must check one-to-one parity, not single happy-path
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [data-migration, testing, completeness]
---

When migrating data from one artifact/schema to another (e.g., report rows to dataset queues), parity testing must cover all existing rows in source, not just a single document. Happy-path tests can miss silent data loss when aggregating the old artifact after migration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
