---
name: crossprovider codex stale-plan-claims-without-live-discovery-become-
description: Stale plan claims without live discovery become unusable artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-23
  tags: [planning, data-discovery, governance]
---

Plans that assert filesystem state ("61 root entries", "llm-wiki-mkt-a exists") without re-running live discovery become flagged as unusable when directory contents drift. In this case, a June 14 plan was stalled in review because a June 22 live check showed 63 entries + llm-wiki-mkt-a instead. Always re-run discovery before any planning claim about data state; inherited counts from older probes are grounds for rejection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
