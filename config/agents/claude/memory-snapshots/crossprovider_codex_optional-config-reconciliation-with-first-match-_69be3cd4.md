---
name: crossprovider codex optional-config-reconciliation-with-first-match-
description: Optional config reconciliation with first-match alias fallback is fail-open
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, optional-config, forward-compatibility]
---

When reconciling against optional future config using field-name aliases for forward compatibility, accepting the first matching alias without validating subsequent aliases allows contradictory policies to pass. Full policy validation must check all relevant paths; first-match acceptance is insufficient.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
