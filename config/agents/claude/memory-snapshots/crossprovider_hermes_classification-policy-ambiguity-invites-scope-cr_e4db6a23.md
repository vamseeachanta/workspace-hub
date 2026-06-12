---
name: crossprovider hermes classification-policy-ambiguity-invites-scope-cr
description: Classification policy ambiguity invites scope creep
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning, scope-definition, governance]
---

Leaving "which packages must be classified, which ignored" open-ended (e.g., "internal files, shims, empty dirs, _compat, analysis, etc.") creates scope creep. Define allowlist and deliberate exclusions up front. Make classification policy explicit in plan, not implementation-time decisions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
