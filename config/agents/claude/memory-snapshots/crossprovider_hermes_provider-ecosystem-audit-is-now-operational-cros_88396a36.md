---
name: crossprovider hermes provider-ecosystem-audit-is-now-operational-cros
description: Provider ecosystem audit is now operational cross-provider capability
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [operational-capability, provider-monitoring, audit-pipeline]
---

The provider-session-ecosystem-audit skill ingests logs/orchestrator/{provider}/*.jsonl streams and produces canonical JSON+markdown reports tracking session counts, post records, and Python/uv token usage per provider (Claude/Codex/Hermes/Gemini). Use for activity baselines and cross-provider imbalance detection.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
