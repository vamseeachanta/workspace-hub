---
name: crossprovider hermes zero-contention-parallel-agent-output-partitioni
description: Zero-contention parallel-agent output partitioning for same-repo work
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-agents, architecture, git-contention, multi-provider]
---

For N independent parallel agents writing to the same repo, partition outputs uniquely per agent to eliminate git contention: `docs/plans/<audit>/<date>/swarm-<n>-<descriptor>.md` (reports) + `logs/swarm-<n>-<provider>.jsonl` (telemetry). Each agent owns its output path; no synchronization barriers needed. Pattern generalizes across Claude, Codex, Gemini, and Hermes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
