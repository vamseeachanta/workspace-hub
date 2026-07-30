---
name: crossprovider codex range-scoped-legal-scan-when-tree-scan-is-blocke
description: Range-scoped legal scan when tree scan is blocked
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [legal-scan, debt, workaround]
---

Pre-existing violations in unrelated legacy code (170+ in this case) can block full-tree legal scans. Workaround: run range-scoped scan on changed files only against the same deny lists. Document inherited scanner debt explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
