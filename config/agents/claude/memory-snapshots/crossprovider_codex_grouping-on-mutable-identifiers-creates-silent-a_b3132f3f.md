---
name: crossprovider codex grouping-on-mutable-identifiers-creates-silent-a
description: Grouping on mutable identifiers creates silent aggregation data loss
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-loss, aggregation, testing]
---

Grouping on display names (field_name, operator_name, lease_name) instead of stable numeric codes splits one asset into multiple rows when names vary by spelling, abbreviation, or historical change. Must test with realistic operator name variants and historical changes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
