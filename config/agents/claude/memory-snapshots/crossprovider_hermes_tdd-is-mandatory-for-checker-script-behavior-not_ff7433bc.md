---
name: crossprovider hermes tdd-is-mandatory-for-checker-script-behavior-not
description: TDD is mandatory for checker/script behavior, not optional
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, test-driven-development, repo-structure]
---

Checker implementations require RED-first TDD: write failing test → observe RED state → implement → verify GREEN. This pattern is a hard gate for repo-structure enforcement scripts and similar contract-checking tools.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
