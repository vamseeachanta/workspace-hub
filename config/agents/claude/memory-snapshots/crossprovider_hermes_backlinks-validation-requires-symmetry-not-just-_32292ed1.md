---
name: crossprovider hermes backlinks-validation-requires-symmetry-not-just-
description: Backlinks validation requires symmetry, not just presence
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [graph-validation, bidirectional-edges]
---

Emitting a `backlinks` field on nodes is not validation. Validator must check that each node's backlinks exactly match the inverse of all edges pointing to it (sorted, unique, corpus-consistent). Generator sampling + validator presence-check leaves a regression hole. Add validator enforcement: for each node, assert `set(node.backlinks) == {sources of edges targeting this node}`.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
