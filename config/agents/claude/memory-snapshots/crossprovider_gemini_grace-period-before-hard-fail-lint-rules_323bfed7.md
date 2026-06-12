---
name: crossprovider gemini grace-period-before-hard-fail-lint-rules
description: Grace period before hard-FAIL lint rules
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [linting, ci-cd, config-drift]
---

Introducing hard-FAIL lint checks on existing violations immediately breaks CI. Either (a) fix all violations upfront in same PR, or (b) start with WARN + explicit grace period before upgrading to FAIL. Prevents false positives and gives teams time to remediate.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
