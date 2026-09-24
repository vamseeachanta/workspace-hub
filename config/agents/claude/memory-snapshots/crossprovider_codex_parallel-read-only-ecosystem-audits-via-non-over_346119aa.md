---
name: crossprovider codex parallel-read-only-ecosystem-audits-via-non-over
description: Parallel read-only ecosystem audits via non-overlapping write paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [parallel-work, governance, workflow]
---

Large governance audits scale via parallel swarms with disjoint write scopes (e.g., swarm-1 → live-state audit, swarm-2 → capability gaps, swarm-3 → approval drift). Pattern: each swarm writes to `docs/plans/agent-swarm-audits/<date>/swarm-N-*.md` only. Eliminates contention.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
