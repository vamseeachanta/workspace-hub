---
name: crossprovider codex date-based-field-eligibility-must-check-both-for
description: Date-based field eligibility must check both forward and backward bounds against current date
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [date-validation, boundary-testing, temporal-logic]
---

Fields with date values (e.g., 'retrieved_on', 'valid_from') that gate eligibility must be compared against the current evaluation date at runtime, not just parsed and trusted. Boundary tests must cover N-1, N, N+1 conditions (e.g., day 89 passes, day 90 passes, day 91 fails) to catch off-by-one errors. Production code should supply `date.today()` or equivalent at the validation point, not rely on caller dates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
