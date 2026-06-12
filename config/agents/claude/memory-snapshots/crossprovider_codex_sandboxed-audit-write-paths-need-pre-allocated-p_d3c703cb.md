---
name: crossprovider codex sandboxed-audit-write-paths-need-pre-allocated-p
description: Sandboxed audit write-paths need pre-allocated parent dirs
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [sandbox, write-failures, isolation]
---

When execution contexts are governance/audit-only with a single allowed write-path (e.g., `docs/plans/agent-swarm-audits/...`), parent directories cannot be created via `mkdir` in bwrap isolation. Pre-allocate empty parent dirs, use fallback GitHub writes, or accept artifact-write failures in constrained sandboxes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
