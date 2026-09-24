---
name: crossprovider codex script-plans-require-explicit-exit-code-contract
description: Script plans require explicit exit-code contracts and pseudocode
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, scripts, shell, verification]
---

Non-trivial scripts (especially those used in cron or with conditional downstream logic) must define exit-code truth tables distinguishing success-with-findings from operational failures. Plans also need pseudocode blocks and 3+ concrete test cases before approval.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
