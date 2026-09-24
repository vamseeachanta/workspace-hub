---
name: crossprovider codex smoke-test-validation-must-check-schema-not-just
description: Smoke test validation must check schema, not just file existence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, artifact-validation, acceptance-criteria]
---

Verifying that 9 report files exist is not equivalent to validating acceptance criteria. Tests must validate the full artifact contract: correct schema, non-empty content, parseable structure. Existence-only checks hide incomplete implementations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
