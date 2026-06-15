---
name: crossprovider codex coverage-status-vocabulary-must-be-identical-acr
description: Coverage/status vocabulary must be identical across plan, tests, and schema
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [planning, testing, vocabulary]
---

If a plan requires sources to end in {extracted, skipped, deferred, gated, manual, blocked}, but a test checks for {extracted, ignored, pending, gated, manual, blocked}, acceptance criteria become un-verifiable. Standardize vocabulary in one place (schema or enum) and use it in plan acceptance criteria, test assertions, and implementation code.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
