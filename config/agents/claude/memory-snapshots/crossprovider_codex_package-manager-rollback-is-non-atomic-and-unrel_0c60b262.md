---
name: crossprovider codex package-manager-rollback-is-non-atomic-and-unrel
description: Package manager rollback is non-atomic and unreliable without pre-state recording
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [operations, rollback, dependency-management]
---

npm install -g pkg@previous does not guarantee state restoration: transitive dependencies change, cache may be stale/poisoned, postinstall scripts can behave differently between versions, and binary shims may mismatch. Rollback needs pre-update snapshots (exact transitive deps, postinstall output, shim hash), deterministic restore, and post-restore verification to catch partial failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
