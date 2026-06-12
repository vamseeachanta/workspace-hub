---
name: crossprovider hermes log-naming-contract-mismatches-cause-false-negat
description: Log naming contract mismatches cause false-negative health checks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [logging, health-checks, ecosystem-audit]
---

Scripts write audit logs as 'parity-review-*.md' but health checkers look for 'cron-*.log'; mismatches cause false MISSING verdicts. Define log contracts upfront; add lint rules to enforce naming consistency.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
