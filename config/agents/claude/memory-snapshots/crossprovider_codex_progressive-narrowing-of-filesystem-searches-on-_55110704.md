---
name: crossprovider codex progressive-narrowing-of-filesystem-searches-on-
description: Progressive narrowing of filesystem searches on large repos
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [performance, discovery, operations]
---

Broad recursive filesystem scans timeout on large or slow mounts. Start wide, but pivot quickly to path-limited and git-history checks (git log with path filters, git object lists) when initial scans stall. Verify nonexistence via git history, not just missing from current checkout.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
