---
name: crossprovider codex alias-field-validation-must-check-all-alternativ
description: Alias-field validation must check all alternatives for consistency
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [validation, fail-closed, config-schema, security-pattern]
---

In config reconciliation, using `_first_present_list()` to accept the first matching alias field while ignoring later contradictory aliases creates a fail-open vulnerability. Validation must check ALL named paths to the same data for consistency—if one alias is correct but another contradictory alias is present, reject the whole record.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
