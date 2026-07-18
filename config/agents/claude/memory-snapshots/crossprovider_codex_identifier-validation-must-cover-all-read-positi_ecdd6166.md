---
name: crossprovider codex identifier-validation-must-cover-all-read-positi
description: Identifier validation must cover ALL read positions, not hardcoded slots
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [config-driven-validation, security-gaps, completeness]
---

If primary keys, canonical paths, or metadata columns are configuration-driven but validation checks only hardcoded positions (e.g., identifiers[2:]), misconfigured column names can bypass content-type guards. Validate forbidden content across all identifier sources regardless of position.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
