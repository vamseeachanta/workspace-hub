---
name: crossprovider codex codex-sandbox-bwrap-loopback-failure-blocks-shel
description: Codex sandbox bwrap loopback failure blocks shell and local writes
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [codex-sandbox, tooling-quirk, workaround]
---

Recurring `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted` blocks all shell execution and local file writes in Codex sandbox across multiple sessions (2026-05-20 through 2026-05-21). GitHub connector inspection remains viable as fallback. When blocked, switch to read-only GitHub connector for branch/file inspection and reserve local writes for critical fallback only.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
