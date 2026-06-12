---
name: crossprovider hermes cron-automation-jobs-need-concrete-artifact-path
description: Cron/automation jobs need concrete artifact paths and first-run contracts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [automation, cron, deliverables, contracts]
---

Automated jobs must define: concrete artifact output paths (not just types), behavior on first run (when prior artifact doesn't exist), deterministic ordering of outputs. Leaving these open causes implementation drift and makes outputs unstable across runs. State these as explicit acceptance criteria.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
