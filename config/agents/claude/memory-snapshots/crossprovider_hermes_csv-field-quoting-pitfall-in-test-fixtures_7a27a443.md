---
name: crossprovider hermes csv-field-quoting-pitfall-in-test-fixtures
description: CSV field quoting pitfall in test fixtures
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, csv-format, data-validation]
---

Embedded newlines in CSV string field values without proper quoting cause row-count mismatches in tests. Ensure test fixtures either escape newlines, quote fields containing them, or remove newlines entirely. This breaks row-counting validation logic.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
