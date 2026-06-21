---
name: crossprovider codex test-coverage-gaps-between-code-logic-and-genera
description: Test coverage gaps between code logic and generated artifact output — need separate artifact verification tests
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [testing-gaps, artifact-verification, generated-files]
---

Code may define correct enums/logic but generated reports/HTML may not render all cases (e.g., zero-count buckets, all routing outcomes). Logic tests cover happy path; need artifact tests that verify the generated file actually contains expected fields/buckets, not just that the builder ran.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
