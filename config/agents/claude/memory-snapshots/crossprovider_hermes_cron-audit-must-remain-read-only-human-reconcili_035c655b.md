---
name: crossprovider hermes cron-audit-must-remain-read-only-human-reconcili
description: Cron audit must remain read-only; human reconciliation needs explicit classification
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [auditing, cron-jobs, reconciliation, workflows]
---

Weekly skill audit script (cron-owned) must stay deterministic and read-only—no recurring mutation of tracked files. Human reconciliation uses a separate script to classify each filesystem-only skill as: (1) promote/commit, (2) archive, (3) ignore with rationale, or (4) delete as junk. This separation prevents cron pollution and keeps disposition logic auditable.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
