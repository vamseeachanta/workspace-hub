---
name: crossprovider codex issue-success-criteria-must-be-externally-valida
description: Issue success criteria must be externally validated, not synthetic
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, benchmarking, spec-closure]
---

Synthetic workbook examples prove formula implementation, not real-world improvement. Before claiming a criterion met, add a reproducible benchmark using actual sourced inputs and compare against an external reference (e.g., public filing, vendor result, peer measurement). If sourced inputs are unavailable, explicitly report that success is undetermined rather than claiming it.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
