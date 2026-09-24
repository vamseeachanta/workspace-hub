---
name: crossprovider gemini multi-provider-gate-logging-requires-legacy-exem
description: Multi-provider gate logging requires legacy exemption discriminator
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [governance, logging, gate-enforcement, backward-compat]
---

When enforcing new logging contracts across provider agents retroactively, use a two-tier discriminator: WRK ID threshold (e.g., WRK-658+) + created_at datetime cutoff. This prevents backward compatibility breaks for pre-contract work while ensuring new work is audited. Set cutoff as a named constant (e.g., LOG_GATE_SINCE) for maintainability.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
