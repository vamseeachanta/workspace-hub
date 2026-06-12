---
name: crossprovider hermes public-safety-artifact-leakage-has-multiple-orth
description: Public-safety artifact leakage has multiple orthogonal modes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [public-safety, artifact-generation, validation]
---

Three independent leakage vectors found in llm-wiki public-graph artifacts: (1) agent-instruction surfaces in unresolved target_ref from malformed frontmatter parsing, (2) sentence-fragment prose copied into target_ref fields (regex too greedy), (3) 51% unresolved edges with no scope/freshness validation. Fixing one mode doesn't catch the others.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
