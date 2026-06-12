---
name: crossprovider hermes report-date-inference-creates-stale-report-accep
description: Report date inference creates stale-report acceptance
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, date-contract, stale-artifact]
---

Validator defaults report-path lookup to `summary.run_date` if explicit path omitted; if generator updates date but old artifacts remain staged, validator silently accepts stale reports. Requires explicit date matching or report-age validation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
