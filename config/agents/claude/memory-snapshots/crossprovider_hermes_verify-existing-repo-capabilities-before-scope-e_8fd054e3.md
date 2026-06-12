---
name: crossprovider hermes verify-existing-repo-capabilities-before-scope-e
description: Verify existing repo capabilities before scope expansion
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [scope-creep, code-reuse, capability-discovery]
---

Plans proposing new scripts/helpers often miss that repo already carries required fields/logic. Example: plan #2249 proposes decomposition script but index.jsonl already has path_category/path_subcategory fields, and enrich-category.py exists. Check existing surfaces before approving new tools.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
