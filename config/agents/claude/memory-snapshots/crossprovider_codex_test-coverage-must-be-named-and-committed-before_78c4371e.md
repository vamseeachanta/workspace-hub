---
name: crossprovider codex test-coverage-must-be-named-and-committed-before
description: Test coverage must be named and committed before plan approval
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [testing, governance, acceptance-criteria]
---

Don't assume existing tests cover generated artifacts (wiki pages, reports). Leakage/citation validators for each output type must be written and explicitly named in plan's 'Files to Change' section before approval. Unnamed or missing test coverage is a MAJOR blocker.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
