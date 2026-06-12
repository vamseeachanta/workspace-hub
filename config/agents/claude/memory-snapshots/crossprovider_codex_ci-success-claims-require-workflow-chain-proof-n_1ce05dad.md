---
name: crossprovider codex ci-success-claims-require-workflow-chain-proof-n
description: CI success claims require workflow chain proof, not assumption
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [ci-design, proof-obligation, testing]
---

Plans asserting first-run CI will be green must show how coverage.json gets generated, prove all gate dependencies are satisfied, and trace the full command chain. Local tests passing does not imply CI will pass; each gate artifact must be accounted for.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
