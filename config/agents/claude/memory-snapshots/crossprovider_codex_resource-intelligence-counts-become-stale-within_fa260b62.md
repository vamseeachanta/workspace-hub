---
name: crossprovider codex resource-intelligence-counts-become-stale-within
description: Resource-intelligence counts become stale within hours after concurrent repo commits
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [resource-intelligence, staleness, plan-review, accuracy]
---

Plans with stable-looking resource counts (entry totals, file-path assertions) lose freshness rapidly when parallel commits land. Example: sitemap entry count stated as 33 at plan commit time but actually 39 after concurrent additions. Plans need freshness verification against current repo state, not assumed-stable resource claims.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
