---
name: crossprovider hermes documentation-drift-in-multi-agent-systems-confi
description: Documentation drift in multi-agent systems: config-as-stale until verified
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-agent, documentation-drift, config-drift, verification]
---

Agent-written documentation (e.g., 'agents.md says Hermes maintains 691 skills in ~/.hermes') diverges from actual architecture changes. Agents cannot introspect live state; durable sync requires periodic audit + verification of claimed vs. actual setup, not trust of docs written at prior time.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
