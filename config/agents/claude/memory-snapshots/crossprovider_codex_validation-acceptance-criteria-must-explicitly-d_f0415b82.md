---
name: crossprovider codex validation-acceptance-criteria-must-explicitly-d
description: Validation acceptance criteria must explicitly distinguish pass/fail/skipped
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [adversarial-review, acceptance-criteria, validation, closeout-logic]
---

Plans for validation-heavy issues allow closing with 'failures captured' when acceptance actually requires 'validation passed'. This creates ambiguous closeout conditions. Validation plans must include an explicit decision tree (IF validation_attempted THEN {PASS|FAIL} ELSE {skip_reason}) so failure documentation cannot satisfy pass criteria.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
