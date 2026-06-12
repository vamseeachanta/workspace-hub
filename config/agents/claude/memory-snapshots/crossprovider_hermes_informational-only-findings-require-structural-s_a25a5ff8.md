---
name: crossprovider hermes informational-only-findings-require-structural-s
description: Informational-only findings require structural separation, not just flags
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [design, reporting, audit, separation-of-concerns]
---

Marking findings with `informational_only=True` is insufficient; they must be bucketed into a separate report section (e.g., 'Suppressed / Carry-Forward Findings'). If left in ranked active findings, they still appear as false positives. For tiered-severity audit reports, enforce structural separation at the reporting layer, not just data annotation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
