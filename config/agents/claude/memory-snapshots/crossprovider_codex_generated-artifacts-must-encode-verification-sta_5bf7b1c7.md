---
name: crossprovider codex generated-artifacts-must-encode-verification-sta
description: Generated artifacts must encode verification state, not placeholder text
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [spec-compliance, generated-artifacts, schema-parity, testing]
---

When specs require "active" or "verified" status, generated artifacts using placeholder text like "not-evaluated-in-artifact" fail spec compliance even if tests pass. Tests encode implementation behavior; spec compliance requires generated state fields to reflect verification evidence. Also applies to schema field names: tests can pass with wrong field names (standard_status vs regulatory_status) if testing implementation, not spec.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
