---
name: crossprovider gemini operating-model-tier-assignments-require-explici
description: Operating-model tier assignments require explicit cross-machine sync direction
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [cross-machine, tier-assignment, operating-model]
---

Plans for multi-machine tools must include a tier-assignment table: git-tracked (L1/authoritative), shared-mount (L2/preferred-when-reachable), local-cache (L3/not-authoritative). Checkpoint state should be L2 (shared mount) if resumable across machines; L3 if local-only. This prevents tier-confusion during implementation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
