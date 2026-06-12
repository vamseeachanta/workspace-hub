---
name: crossprovider codex first-run-and-real-corpus-acceptance-testing-def
description: First-run and real-corpus acceptance testing deferred to manual/reviewer-task
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, first-run, acceptance-criteria]
---

Plans use fixture-based tests to cover acceptance criteria but defer real-corpus or first-run validation to 'reviewer approval' or 'integration smoke test', leaving correctness-critical behavior unautomated. Every AC must have an executable test; manual smoke tests are supplementary, not primary coverage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
