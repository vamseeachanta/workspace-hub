---
name: crossprovider codex agent-yaml-metadata-has-timestamp-only-and-uuid-
description: Agent YAML metadata has timestamp-only and UUID-only churn
metadata:
  type: reference
  source: codex
  bridged: 2026-06-17
  tags: [agent-config, test-fixtures, noise-in-diffs]
---

Agent config and test fixture diffs often show only timestamp or UUID changes (e.g., Plotly template UUIDs, agent.yaml dates) with no semantic change. Filter these in pre-commit or normalize with fixed seeds before diffs to avoid noise.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
