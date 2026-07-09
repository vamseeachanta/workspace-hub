---
name: crossprovider codex external-data-apis-undergo-schema-drift-validate
description: External data APIs undergo schema drift; validate before adapter implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-05
  tags: [data-engineering, external-source-reliability, schema-validation]
---

ANP Brazil production API shifted from endpoint URL `consulta-producao-por-poco` (returns 404) to new endpoint, changed columns from lowercase `oleo_sm3` (Sm³ totals) to `Óleo (bbl/dia)` (Spanish label, bbl/day daily rate), and changed units from monthly/cumulative to daily. Do not commit to an adapter until verifying the live endpoint, fetching actual sample rows, and testing column expectations against real data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
