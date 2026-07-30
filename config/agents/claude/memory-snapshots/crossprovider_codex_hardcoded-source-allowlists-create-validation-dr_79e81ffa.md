---
name: crossprovider codex hardcoded-source-allowlists-create-validation-dr
description: Hardcoded source allowlists create validation drift
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [config-management, duplication, contracts]
---

When metadata evidence paths are hardcoded in production (e.g., FIXED_METADATA_EVIDENCE_PATHS) instead of loaded from a contract config, contract changes aren't reflected in the scanner allowlist. This causes manifest validation to accept sources that the public-scan allowlist rejects, creating a mismatch.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
