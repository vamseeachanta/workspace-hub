---
name: crossprovider hermes broad-pattern-rules-require-exception-tests-to-p
description: Broad pattern rules require exception tests to prevent false positives
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, pattern-matching, false-positives, validation]
---

When implementing rules that match broad patterns (prefix checks, directory references), include explicit negative test cases for legitimate exceptions. Otherwise, valid paths matching the pattern get incorrectly flagged. Example: checking for `knowledge/wikis/` references in code flags both stale imports AND intentional historical documentation references without a way to distinguish them.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
