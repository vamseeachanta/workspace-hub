---
name: crossprovider hermes pre-lock-state-reset-creates-race-conditions-in-
description: Pre-lock state reset creates race conditions in concurrent shell watchers
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [shell-scripting, concurrency, locking, bug-pattern]
---

Initializing or resetting shared-state files before acquiring a lock allows concurrent no-op invocations to mutate state of the active process. watch-results.sh was resetting git-pull-failures.count before acquiring flock, so a second concurrent invocation would erase the active watcher's failure counter even though it immediately exited. Acquire the lock first, then initialize shared state.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
