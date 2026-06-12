---
name: crossprovider hermes commit-grouping-by-coherence-dependency-order
description: Commit grouping by coherence + dependency order
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, commit-strategy]
---

When multiple changes are in-tree, group commits by functional unit (e.g., logger persistence + its test), then order by logical dependency (infrastructure/persistence first, then tests/outputs consuming it, then separate concerns like docs/planning). Rationale for each group's position clarifies why it cannot be earlier.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
