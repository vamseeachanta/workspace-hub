---
name: crossprovider hermes audit-interpretation-requires-previous-audit-par
description: Audit interpretation requires previous_audit parameter for trends
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [audit, architecture, parameter-design]
---

`build_provider_interpretation_summary()` must accept `previous_audit: dict | None` to enable trend comparisons (activity, debt, drift, python hygiene). Comparisons require prior data extraction of recent post/session counts and python hygiene metrics from the previous audit snapshot.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
