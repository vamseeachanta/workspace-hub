---
name: crossprovider codex plans-diverge-from-live-implementation-in-parall
description: Plans diverge from live implementation in parallel work
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [planning, contracts, coordination]
---

When implementation issues (#62-#72) land contracts/scanners concurrently, plans can become stale against current artifacts within days. Always re-verify plan assumptions (dependencies, contract shapes, validator outputs) against live config/script/test files before declaring plan-review ready.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
