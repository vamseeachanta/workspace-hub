---
name: crossprovider codex reusable-contract-pattern-json-config-python-val
description: Reusable contract pattern: JSON config + Python validator + test module + CI integration
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture-pattern, contract-design, reusable-structure]
---

Across approved gates, the pattern is consistent: each contract has a `config/*.json`, matching `scripts/validate_*.py` validator, dedicated `tests/test_validate_*.py` with focused coverage, and public-surface scan integration. This is the durable mold for new issues to follow.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
