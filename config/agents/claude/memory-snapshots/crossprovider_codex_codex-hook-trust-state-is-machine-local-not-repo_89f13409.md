---
name: crossprovider codex codex-hook-trust-state-is-machine-local-not-repo
description: Codex hook trust state is machine-local, not repo-traveled
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex, hooks, deployment, portability]
---

Hook review trust (trusted_hash in ~/.codex/config.toml) is user-machine local by design and does not travel with repo-tracked hook commands. Each machine must independently review and trust hooks; this is appropriate because hooks execute shell commands and require per-machine approval.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
