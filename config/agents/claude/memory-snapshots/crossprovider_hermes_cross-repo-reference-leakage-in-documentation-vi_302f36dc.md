---
name: crossprovider hermes cross-repo-reference-leakage-in-documentation-vi
description: Cross-repo reference leakage in documentation violates privacy
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [privacy, documentation, references]
---

Strategic documentation can embed workspace-internal references (workspace-hub paths, GitHub Issue IDs like WRK-*, GitHub Actions, GitHub Issues terminology) that should be generic or internal only. Audit docs for these patterns and replace with generic terms (e.g., 'internal workstream', 'internal tracking system').

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
