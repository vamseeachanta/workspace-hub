---
name: crossprovider codex acceptance-criterion-completeness-smoke-tests-mu
description: Acceptance criterion completeness: smoke tests must enumerate all required inputs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [acceptance-criteria, prechecks, required-inputs]
---

Pre-approval smoke tests must check the existence of ALL required inputs before executing the main logic, not a subset. If a plan lists N required inputs but smoke test only prechecks N-1, acceptance can pass pre-implementation while the implementation path will fail on the unchecked input.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
