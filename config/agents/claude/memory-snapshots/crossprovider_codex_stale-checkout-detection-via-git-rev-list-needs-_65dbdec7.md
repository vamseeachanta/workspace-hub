---
name: crossprovider codex stale-checkout-detection-via-git-rev-list-needs-
description: Stale-checkout detection via git rev-list needs recent fetch state
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, merge, safety, distributed-systems]
---

`git rev-list HEAD..origin/main` without a recent `git fetch` can false-negative and incorrectly report a checkout as current when the remote has advanced. Either include a provenance field proving `origin/main` was freshly fetched, or fail closed if that cannot be established.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
