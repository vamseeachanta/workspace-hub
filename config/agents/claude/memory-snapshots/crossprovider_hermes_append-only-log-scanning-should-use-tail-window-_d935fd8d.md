---
name: crossprovider hermes append-only-log-scanning-should-use-tail-window-
description: Append-only log scanning should use tail window, not full scan
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [logging, debugging, pattern-matching]
---

Avoid false positives in error pattern scanning over append-only logs. Scan recent tail (last 100–200 lines) only. Full scan includes historical noise and unrelated transient errors from prior runs; tail captures current-session state.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
