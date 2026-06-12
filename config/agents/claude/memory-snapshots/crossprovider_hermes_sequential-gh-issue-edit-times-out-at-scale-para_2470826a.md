---
name: crossprovider hermes sequential-gh-issue-edit-times-out-at-scale-para
description: Sequential gh issue edit times out at scale; parallel operations required
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-api, automation, performance]
---

Bulk labeling 175+ GitHub issues via sequential `gh issue edit` calls hits API timeout (~300s). Parallel curl requests with GitHub REST API (batched) completed 175 labels in <30s. For any bulk GitHub mutation task >50 items, use parallel/bulk approach not CLI loops.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
