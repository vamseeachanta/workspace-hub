---
name: crossprovider codex bounded-enumeration-prevents-dos
description: Bounded enumeration prevents DoS
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [performance, security, dos-prevention, directory-operations]
---

Use scandir (streaming enumeration with early-exit) to enforce member-count limits before materializing the full directory. Never use listdir + sort without a pre-check limit. Unbounded enumeration is a DoS vector and allows attacker-controlled path work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
