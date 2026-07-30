---
name: crossprovider codex safety-state-must-bind-to-inodes-leases-not-name
description: Safety state must bind to inodes/leases, not names or booleans
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [design, safety, concurrency]
---

In concurrent/safety-critical code, name-based or boolean safety flags are insufficient. State must be enforced through inode-bound leases or atomic file-handle primitives that survive process restarts and guarantee atomicity across concurrent access.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
