---
name: crossprovider codex related-completed-issues-must-be-cited-for-patte
description: Related completed issues must be cited for pattern carryover
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, related-issues, implementation-patterns, carryover]
---

When a related completed issue provides implementation patterns or constraints (key filtering, API usage, test structure), omitting it from plan citations creates silent regressions or redundant work. Example: plan #611 references issue #468 in the GitHub issue body but omits it from Sources Consulted, leading to loss of the API-key-filtering pattern that prevents test-to-production divergence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
