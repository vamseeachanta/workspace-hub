---
name: crossprovider codex link-graph-ci-gates-catch-orphan-regressions-in-
description: Link-graph CI gates catch orphan regressions in published sites
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [ci, testing, frontend]
---

Published-site broken hrefs (e.g., decommissioning→intervention-db 404) ship silently without automated tests. CI must walk the link graph and fail if orphans or dead-ends exist post-publication.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
