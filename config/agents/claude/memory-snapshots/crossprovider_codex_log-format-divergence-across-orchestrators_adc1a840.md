---
name: crossprovider codex log-format-divergence-across-orchestrators
description: Log format divergence across orchestrators
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [logging, normalization, cross-provider, governance]
---

Claude and Codex emit logs in YAML key-value format; Gemini uses ISO8601+INFO markers. Standardization required for consistent log parsing and orchestrator comparison. WRK-675 identified this as a drift requiring normalization.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
