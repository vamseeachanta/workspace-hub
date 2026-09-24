---
name: crossprovider codex privacy-validation-must-constrain-both-field-str
description: Privacy validation must constrain both field structure and value source
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [privacy, validation, security]
---

Row-level field validation doesn't guarantee privacy if unconstrained fields in the same structure can be populated from untrusted sources. Synthetic probes with client names, emails, counts, and file-like values passed validation when placed in allowed fields. Semantic-index metadata bypass occurred because top-level fields were copied without the same denylist constraints applied to row fields.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
