---
name: crossprovider codex identity-naming-consistency-across-components-pr
description: Identity/naming consistency across components prevents mismatch bugs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-modeling, identity-drift, validation]
---

When scheduler jobs, output directories, metadata module IDs, and contract row names lack explicit aliases or validation, identity drift occurs (EIA: scheduler outputs `data/modules/eia` but contract row is "EIA US"). Require module_id fields, validator checks for mismatches, or explicit alias mappings.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
