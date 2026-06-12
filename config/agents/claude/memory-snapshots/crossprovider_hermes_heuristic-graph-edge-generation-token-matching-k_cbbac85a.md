---
name: crossprovider hermes heuristic-graph-edge-generation-token-matching-k
description: Heuristic graph edge generation (token matching, keyword inference) is brittle for stable downstream contracts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [graph-design, v1-scope, brittleness]
---

Cross-link edges inferred via token matching + free-text keyword relation-typing are title-sensitive and drift when pages are renamed or new similarly-named pages appear. For v1 stable contracts, prefer either explicit semantic schema or bounded deterministic scope over probabilistic heuristics.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
