---
name: crossprovider codex github-connector-search-omits-label-details-use-
description: GitHub connector search omits label details; use direct issue fetches
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [api-limitation, github-connector, tooling]
---

Issue search endpoint returns body but not full label metadata. When label verification is required, fetch specific issues directly instead of relying on aggregated search results.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
