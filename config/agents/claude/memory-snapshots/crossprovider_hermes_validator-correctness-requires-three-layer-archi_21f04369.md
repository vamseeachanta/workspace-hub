---
name: crossprovider hermes validator-correctness-requires-three-layer-archi
description: Validator correctness requires three-layer architecture
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, architecture, public-graph]
---

Single-layer consistency checks miss critical bugs: (1) scope enforcement—is every node/input allowlisted?, (2) deterministic field verification—do edge_id/digests recompute correctly?, (3) freshness check—does corpus mutation invalidate artifacts? Design validators with all three or document scope explicitly.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
