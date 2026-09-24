---
name: crossprovider codex codex-sandbox-path-restrictions-for-result-artif
description: Codex sandbox path restrictions for result artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex, tooling-quirk, sandbox-limitations]
---

Codex session result files cannot be written outside the project worktree. Writes to shared log directories (e.g., `/mnt/local-analysis/agent-logs/*/results/`) are rejected by the sandbox. Result artifacts must be written within the repo tree or designated writable roots.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
