---
name: crossprovider codex agent-instruction-contracts-must-map-unambiguous
description: Agent instruction contracts must map unambiguously to code
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [agent-design, contracts, silent-failures, correctness]
---

When instruction contracts tell agents what to output (e.g., 'return verified'), ensure the vocabulary maps cleanly to downstream code expectations (e.g., specific enum values or status constants). Ambiguous mappings cause silent failures and incorrect outcomes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
