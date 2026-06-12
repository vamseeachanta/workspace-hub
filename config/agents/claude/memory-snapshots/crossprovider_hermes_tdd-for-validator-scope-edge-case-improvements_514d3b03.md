---
name: crossprovider hermes tdd-for-validator-scope-edge-case-improvements
description: TDD for validator scope/edge-case improvements
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, validation, tdd, llm-wiki]
---

Write failing tests first for validator edge cases (off-scope node rejection, forged edge_id detection, stale artifact detection) before implementing fixes. Validators often appear complete but lack enforcement tests for scope, determinism, and freshness—test failures expose design gaps.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
