---
name: crossprovider codex legacy-entries-outside-managed-blocks-should-fai
description: Legacy entries outside managed blocks should fail verification
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [infrastructure, tdd, governance]
---

Unregistered config/cron entries appended after last cutover are deny-by-default. Write regression test using exact live lines to prove the blocker exists before adding minimal legacy identity records.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
