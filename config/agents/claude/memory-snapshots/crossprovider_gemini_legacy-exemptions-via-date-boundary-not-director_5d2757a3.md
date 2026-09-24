---
name: crossprovider gemini legacy-exemptions-via-date-boundary-not-director
description: Legacy exemptions via date boundary, not directory presence
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [backward-compatibility, gate-design, auditing]
---

When exempting older items from new gates, use a created_at date boundary; directory presence is insufficient and allows bypass. Date-boundary approach is explicit and auditable. WRK-658 v5.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
