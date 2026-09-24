---
name: crossprovider codex hardcoded-production-allowlists-drift-from-confi
description: Hardcoded production allowlists drift from configuration contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-maintenance, configuration-management, validator-pattern]
---

When production code maintains a secondary hardcoded constant or allowlist that parallels a configuration-based contract (e.g., FIXED_METADATA_EVIDENCE_PATHS mirroring manifest source keys), the allowlist becomes stale when the contract changes. Derive allowlists directly from configuration instead of maintaining them as separate constants.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
