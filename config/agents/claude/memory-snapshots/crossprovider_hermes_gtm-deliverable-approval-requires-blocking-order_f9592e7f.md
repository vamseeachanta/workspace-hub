---
name: crossprovider hermes gtm-deliverable-approval-requires-blocking-order
description: GTM deliverable approval requires blocking-order sequencing, not parallel execution
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [gtm-workflow, dependency-sequencing, approval-order]
---

Demo validation (#2118) blocks GIF production (#1809); GIF production blocks outreach messaging (#1669); persona definition blocks downstream GTM work. Sequential gating is load-bearing; attempting parallelization without this order unblocks broken dependencies.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
