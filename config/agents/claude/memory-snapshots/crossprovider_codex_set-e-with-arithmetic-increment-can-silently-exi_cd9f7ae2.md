---
name: crossprovider codex set-e-with-arithmetic-increment-can-silently-exi
description: `set -e` with arithmetic increment can silently exit
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, set-e, subtle-bug]
---

In bash, `(( var++ ))` under `set -e` exits if the expression is falsy. Incrementing from 0→1 is falsy in arithmetic context, triggering unexpected early exit. Common footgun in loop counters under strict mode.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
