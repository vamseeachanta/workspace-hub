---
name: crossprovider hermes local-cron-locking-tested-in-isolation-but-not-w
description: Local cron locking tested in isolation but not wired into entrypoint
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron-safety, lock-enforcement]
---

If `no_overlap_lock()` exists in tests/helpers but `main()` never calls it, concurrent cron invocations are still possible. Presence of helper code ≠ enforcement. Implementation must actually acquire the lock in the runnable path, or document explicitly that an external wrapper (systemd timer, crontab) is responsible.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
