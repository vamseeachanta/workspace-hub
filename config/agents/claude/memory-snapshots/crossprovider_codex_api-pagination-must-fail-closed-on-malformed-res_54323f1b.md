---
name: crossprovider codex api-pagination-must-fail-closed-on-malformed-res
description: API pagination must fail-closed on malformed responses
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [correctness, api-resilience, code-review]
---

Pagination cursors must validate pageInfo presence and endCursor advancement; missing or malformed pageInfo should raise an error rather than silently break. Absence of these guards enables infinite loops and silent data loss. Test coverage must include error cases, not just happy paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
