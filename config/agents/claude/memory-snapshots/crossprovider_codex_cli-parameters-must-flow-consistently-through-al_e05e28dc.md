---
name: crossprovider codex cli-parameters-must-flow-consistently-through-al
description: CLI parameters must flow consistently through all advertised code paths
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [cli-design, api-consistency]
---

A `--contract` parameter accepted on the CLI was honored in direct `--scan-public-path` scans but silently ignored in review-artifact and snapshot scanning modes, which fell back to default contracts. Parameters must either flow through all related modes or be rejected upfront at the CLI boundary.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
