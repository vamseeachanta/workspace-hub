---
name: crossprovider gemini copy-redirect-delete-pattern-for-high-risk-migra
description: Copy→Redirect→Delete pattern for high-risk migrations
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [migration, refactoring, safety]
---

Introduce new structure in parallel, verify runtime works, then remove old trees. Avoids silent breakage from path changes in dispatch, hooks, or cron workflows.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
