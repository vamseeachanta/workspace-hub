---
name: crossprovider hermes provider-dashboard-approval-transactions-must-is
description: Provider-dashboard approval transactions must isolate UI from state mutation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [approval-gates, provider-orchestration, auditability]
---

For approval dashboards that gate provider work (e.g., #2665), separate approval UI/report generation from approval transaction (CLI/API) from dispatcher lease mechanics; avoid direct HTML-button-to-GitHub mutations; static HTML reports with command-link actions + backend validation script is safer and auditable than direct label/comment mutation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
