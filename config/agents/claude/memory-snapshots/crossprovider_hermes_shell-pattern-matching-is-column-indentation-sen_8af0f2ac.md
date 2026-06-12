---
name: crossprovider hermes shell-pattern-matching-is-column-indentation-sen
description: Shell pattern matching is column/indentation sensitive; fails on real code
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [shell-patterns, testing-gap, regex]
---

Regex patterns for matching shell blocks like `if [[ ... ]] ... fi` assume code at column 0. Real hook code is indented, so patterns anchored with `^` fail silently while tests pass on synthetic unindented fixtures. Always test against actual codebase formatting, not normalized test fixtures.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
