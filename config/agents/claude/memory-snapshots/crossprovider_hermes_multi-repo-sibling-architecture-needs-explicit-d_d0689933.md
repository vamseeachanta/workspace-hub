---
name: crossprovider hermes multi-repo-sibling-architecture-needs-explicit-d
description: Multi-repo sibling architecture needs explicit design before implementation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [architecture, multi-repo-design, hermes-integration, design-gate]
---

Sibling-repo designs (registry authority vs. template sources, dev-secondary semantics, approval-marker logic vs. GitHub labels, cross-repo dirty-state strategy) cannot be deferred to implementation. Placeholder answers allow contradictory assumptions to hide until integration fails.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
