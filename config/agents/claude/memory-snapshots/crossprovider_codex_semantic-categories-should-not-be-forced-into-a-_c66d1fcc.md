---
name: crossprovider codex semantic-categories-should-not-be-forced-into-a-
description: Semantic categories should not be forced into a single enumeration
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [schema-design, semantics, data-modeling]
---

Modeling 'source_class as one of {canonical/duplicate/public/synthetic}' violates independent dimensions: canonical/duplicate is a cardinality relationship, while public/synthetic/private/licensed are orthogonal confidentiality and derivation attributes. A single enum prevents deterministic eligibility decisions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
