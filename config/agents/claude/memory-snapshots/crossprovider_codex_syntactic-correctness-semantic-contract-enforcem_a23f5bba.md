---
name: crossprovider codex syntactic-correctness-semantic-contract-enforcem
description: Syntactic correctness ≠ semantic contract enforcement
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, verification, contract-driven]
---

Tests proving CSV/JSON syntax or wheel build success can pass while data fields silently drop or validation remains incomplete. Mutation-test for overclaiming and boundary-escape cases, not just happy path.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
