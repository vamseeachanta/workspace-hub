---
name: crossprovider hermes validator-checks-can-miss-their-own-failure-mode
description: Validator checks can miss their own failure modes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation-logic, scope-enforcement, test-design]
---

llm-wiki validator rejects unresolved targets only if they point to existing public-safe files, allowing off-scope repo-relative markdown targets (docs/reports/**) to pass silently. Validator doesn't reject forbidden-surface references (CLAUDE.md) embedded in unresolved target_ref. Coverage must include all leakage vectors, not just forbidden patterns.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
