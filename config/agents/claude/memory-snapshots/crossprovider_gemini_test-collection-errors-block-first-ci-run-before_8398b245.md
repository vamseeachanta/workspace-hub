---
name: crossprovider gemini test-collection-errors-block-first-ci-run-before
description: Test collection errors block first CI run before execution
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [test-discovery, import-errors, ci-first-run]
---

Import-time failures in test files (e.g., module renames not updated in test imports, missing packages) prevent collection and block the test suite from running. Issue descriptions often underestimate existing test coverage; actual discovery may reveal more tests than described but also reveal collection blockers that prevent any tests from executing.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
