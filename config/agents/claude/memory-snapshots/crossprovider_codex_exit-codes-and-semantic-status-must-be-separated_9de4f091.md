---
name: crossprovider codex exit-codes-and-semantic-status-must-be-separated
description: Exit codes and semantic status must be separated in harness scripts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [harness, exit-codes, spec-clarity, ci-gates]
---

Process-level exit codes (0/1/2/3) and business-logic status enums (pass/warn/fail/skip) are distinct concerns. Conflating them causes ambiguity in CI/cron interpreters and downstream report consumers. Define an explicit mapping table before implementation: which conditions produce which exit code, with JSON status fields matching that contract.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
