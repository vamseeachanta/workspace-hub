---
name: crossprovider hermes singleton-no-overlap-requires-explicit-preventio
description: Singleton/no-overlap requires explicit prevention, not just detection
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [systemd, cron, race-conditions, availability]
---

Plans that only 'detect' duplicate polling/execution are insufficient; they need hard prevention: exact-one-PID verification + restart procedure, or systemd singleton semantics with guaranteed old-PID drain. Detection-only leaves a transient window where duplicates can still fire.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
