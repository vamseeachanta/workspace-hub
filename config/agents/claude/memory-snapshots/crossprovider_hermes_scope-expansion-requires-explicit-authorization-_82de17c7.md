---
name: crossprovider hermes scope-expansion-requires-explicit-authorization-
description: Scope expansion requires explicit authorization; don't infer new bundles from ambiguous repeated prompts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [scope-management, governance, autonomous-agents]
---

The agent correctly refused to launch continuation work for open issues as new bundles, recognizing this would exceed the original scope without explicit approval. Future autonomous agents should enforce this boundary: new targets, even partial ones, require the user to explicitly name them and confirm governance status rather than implying scope from repetitive prompts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
