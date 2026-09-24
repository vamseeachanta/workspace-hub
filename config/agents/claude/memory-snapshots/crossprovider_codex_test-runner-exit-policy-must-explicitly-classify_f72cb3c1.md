---
name: crossprovider codex test-runner-exit-policy-must-explicitly-classify
description: Test runner exit policy must explicitly classify infrastructure vs test failures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-automation, exit-codes, error-classification, WRK-1054]
---

The rule 'exit 0 iff unexpected_failures == 0' is incomplete when pytest can fail before normal test execution (collection errors, missing repo, timeout, uv resolution failure). Define a repo result model upfront with statuses like `passed`, `failed`, `no_tests`, `infra_error`, `missing_repo` and map process signals into that model.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
