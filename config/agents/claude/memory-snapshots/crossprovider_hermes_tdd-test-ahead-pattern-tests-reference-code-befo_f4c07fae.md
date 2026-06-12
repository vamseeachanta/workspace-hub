---
name: crossprovider hermes tdd-test-ahead-pattern-tests-reference-code-befo
description: TDD test-ahead pattern: tests reference code before implementation exists
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tdd, testing, llm-wiki, review-cycle]
---

Graph manifest generator tests reference evidence_dir and collect_readiness functions before they exist in implementation. Patch failures expected as code catches up to test assertions. After fixes, prior review artifacts become stale; re-run adversarial review to catch newly-fixed code defects.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
