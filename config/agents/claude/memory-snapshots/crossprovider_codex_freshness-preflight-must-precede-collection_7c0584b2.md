---
name: crossprovider codex freshness-preflight-must-precede-collection
description: Freshness preflight must precede collection
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [freshness, validation, ordering, fail-closed]
---

Fail-fast on stale checkout BEFORE generating a report (not after). A silent STALE-CHECKOUT report is worse than a loud, actionable rejection. Check origin/main freshness, fail if fetch fails AND local ref is behind/stale.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
