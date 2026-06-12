---
name: crossprovider codex multi-provider-contract-requires-shared-implemen
description: Multi-provider contract requires shared implementation, not variants
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [multi-agent, contract, code-reuse]
---

When enforcing the same contract across Claude/Codex/Gemini, create one shared implementation (e.g., `log-helper.sh`) that all providers source, not provider-specific copies. Variant implementations drift; shared code + explicit sourcing prevents divergence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
