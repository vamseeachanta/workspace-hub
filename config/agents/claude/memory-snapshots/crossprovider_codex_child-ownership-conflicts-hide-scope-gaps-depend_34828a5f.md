---
name: crossprovider codex child-ownership-conflicts-hide-scope-gaps-depend
description: Child ownership conflicts hide scope gaps; dependency table and cited issues must match
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [planning, ownership, scope]
---

When a parent plan assigns feature A to child issue #123, but #123's live GitHub body explicitly owns feature A+B+C, a merge will either orphan B+C or silently expand scope. Pre-merge validation must reconcile parent dependencies against each cited issue's current body, not just titles.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
