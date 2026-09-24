---
name: crossprovider codex validation-group-identity-leakage-via-naming
description: Validation group identity leakage via naming
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, leakage, machine-learning]
---

Project name aliases and synthetic derived rows leak across train/test folds when grouping uses names instead of stable IDs. Example: `Jack St Malo` vs. `Jack/St. Malo (initial phase)` can split opposite folds. Group validation must track immutable IDs ensuring all aliases stay in the same fold.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
