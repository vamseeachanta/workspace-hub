---
name: crossprovider codex self-scan-safe-validation-principle
description: Self-scan-safe validation principle
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, security, self-referential-integrity, anti-pattern]
---

When a plan defines validation rules or scanners (field-name enums, forbidden patterns, token contexts), those rules must be able to validate the plan artifact itself and its acceptance criteria without requiring blanket exemptions or special-case allowlists. This prevents validator-backdoor defects where the rule-setter exempts their own work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
