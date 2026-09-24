---
name: crossprovider codex acceptance-criteria-using-vague-language-for-exa
description: Acceptance criteria using vague language ('for example', 'expected') allow hollow tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, acceptance-criteria, brittleness]
---

Plans using phrases like 'expected include files,' 'for example 0.2 m,' or 'should assert explicitly' in acceptance criteria allow tests to pass without proving the semantic requirement. Tests validate syntax (YAML parses, file exists) rather than semantics (correct fields, correct count, correct mapping). Acceptance criteria must be objectively testable with no placeholder language.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
