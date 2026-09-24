---
name: crossprovider codex plan-front-matter-and-github-issue-labels-can-di
description: Plan front matter and GitHub issue labels can diverge, masking approval gates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, gates, issue-tracking, consistency]
---

Plan files that embed status fields (e.g., `status: plan-review`) in front matter can lag behind authoritative GitHub issue labels (`status:plan-approved`). Before implementation, reconcile these surfaces explicitly; stale plan metadata can hide whether approval gates have actually fired.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
