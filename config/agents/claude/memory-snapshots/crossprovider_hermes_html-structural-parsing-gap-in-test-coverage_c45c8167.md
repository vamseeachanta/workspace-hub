---
name: crossprovider hermes html-structural-parsing-gap-in-test-coverage
description: HTML structural parsing gap in test coverage
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, test-contracts, html-validation]
---

Plans may explicitly require 'parse HTML structurally, not grep substrings,' but tests can pass while only checking substrings (e.g., assertIn for id attributes). Content regressions won't surface until manual review or live breakage. Cross-check that approved specs for test coverage are actually implemented, not just cited.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
