---
name: crossprovider codex architectural-layer-separation-prevents-contract
description: Architectural layer separation prevents contract duplication
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [architecture, contracts, code-reuse]
---

New gates should reuse and extend existing contracts rather than creating parallel scanners. E.g., #63 (publication certification) should consume #66 (token grammar), #68 (generic surface scan), and #69 (legal deny-list) as layers, not redefine token policy or deny-lists independently.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
