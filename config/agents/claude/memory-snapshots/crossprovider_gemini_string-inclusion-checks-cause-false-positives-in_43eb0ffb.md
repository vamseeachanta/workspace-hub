---
name: crossprovider gemini string-inclusion-checks-cause-false-positives-in
description: String inclusion checks cause false positives in word validation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [validation, gate-logic, bug-pattern]
---

Using `"word" in value.lower()` incorrectly matches unintended strings (e.g., `"passed" in "not passed"` returns True). For word validation in gates, use strict equality: `value.lower().strip() == "expected_word"`.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
