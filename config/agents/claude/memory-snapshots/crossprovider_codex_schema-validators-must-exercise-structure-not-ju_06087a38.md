---
name: crossprovider codex schema-validators-must-exercise-structure-not-ju
description: Schema validators must exercise structure, not just check presence
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [schema-validation, negative-testing, contract-enforcement]
---

Validators that check file existence, literal string presence, or field-name presence pass validation without exercising the data. In #266, the taxonomy validator didn't parse rows or test invalid values; in #267, the gate only checked for a literal substring `source_issue: 266`. Real validation requires parsing the data structure, testing negative cases (e.g., unsafe strings, disallowed combinations), and verifying invariant contracts. Build test suites that intentionally pass invalid values and expect validation to reject them.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
