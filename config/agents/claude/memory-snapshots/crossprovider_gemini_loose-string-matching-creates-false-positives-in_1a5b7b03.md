---
name: crossprovider gemini loose-string-matching-creates-false-positives-in
description: Loose string matching creates false positives in gate validators
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [validator-bugs, string-matching, gate-security]
---

Using `"passed" in decision_val.lower()` matches both "passed" and "not passed". Template unfilled-placeholder detection with `\S` catches comments as non-whitespace. Gate validators need strict equality checks and explicit placeholder markers to avoid accepting incomplete or negated fields.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
