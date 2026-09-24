---
name: crossprovider codex external-cleanup-locks-may-persist-without-activ
description: External cleanup locks may persist without active PIDs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cleanup-safety, lock-handling]
---

A `.cleanup-lock` file can exist on the filesystem after a prior session's cleanup process has exited, with no active PID holding it. Cleanup operations should check for and handle stale locks before proceeding, not assume lock presence means active contention.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
