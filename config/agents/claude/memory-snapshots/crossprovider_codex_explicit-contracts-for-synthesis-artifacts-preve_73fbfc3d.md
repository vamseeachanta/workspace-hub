---
name: crossprovider codex explicit-contracts-for-synthesis-artifacts-preve
description: Explicit contracts for synthesis artifacts prevent silent orchestration failures
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [orchestration-patterns, contract-driven, testing]
---

Multi-agent orchestrations need strict contracts: expected output files by name, required content markers, and structured parsing rules. When synthesis expects 9 inputs but silently proceeds with 8, failures hide until integration time. Make counts and content validation explicit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
