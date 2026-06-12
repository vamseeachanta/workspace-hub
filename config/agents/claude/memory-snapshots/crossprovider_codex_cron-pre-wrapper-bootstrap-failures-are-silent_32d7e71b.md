---
name: crossprovider codex cron-pre-wrapper-bootstrap-failures-are-silent
description: Cron pre-wrapper bootstrap failures are silent
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [cron, scheduler, bootstrap-failures]
---

Outer shell redirection (before the wrapper script runs) can fail on clean machines if target log directories don't exist. Tests must prove the full scheduled command works on clean checkout, not just that the wrapper script exists.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
