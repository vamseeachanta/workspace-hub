---
name: crossprovider codex closed-csv-column-vocabulary-prevents-silent-man
description: Closed CSV column vocabulary prevents silent mangling
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [csv-validation, vocabulary, error-detection]
---

Define KNOWN_PARSE_STATUSES upfront and add all new statuses explicitly. Prevents silent mangling of unknown values during _normalize_queue_row by detecting shifted/unknown statuses as explicit errors.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
