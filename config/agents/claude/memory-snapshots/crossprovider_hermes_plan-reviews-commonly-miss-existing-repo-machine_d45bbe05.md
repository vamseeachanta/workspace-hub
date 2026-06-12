---
name: crossprovider hermes plan-reviews-commonly-miss-existing-repo-machine
description: Plan reviews commonly miss existing repo machinery and risk duplication
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning, review-process, duplication-risk]
---

Plans proposing freshness/staleness work ignored existing staleness-scanner.py, doc-freshness-dashboard, and cron staleness-scan entries. Audit repos for prior art (scripts/, docs/dashboards/, cron schedules) before approving new machinery.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
