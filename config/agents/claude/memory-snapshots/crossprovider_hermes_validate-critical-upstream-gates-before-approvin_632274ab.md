---
name: crossprovider hermes validate-critical-upstream-gates-before-approvin
description: Validate critical upstream gates before approving downstream work
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [gates, sequencing, downstream-risk, validation]
---

High-risk downstream artifacts (customer-facing, external releases, outreach materials) should not be approved until upstream validation gates are complete. Building outreach before demos are validated creates credibility risk. Gate sequencing matters; don't approve the output before validating the input.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
