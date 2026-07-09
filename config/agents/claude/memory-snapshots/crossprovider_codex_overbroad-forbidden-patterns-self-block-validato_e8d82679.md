---
name: crossprovider codex overbroad-forbidden-patterns-self-block-validato
description: Overbroad forbidden patterns self-block validators
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [testing, safety-contracts, validation-design]
---

Negative validation patterns (e.g., 'no recursive grep, no os.walk, no .rglob') must have scoped allowlisted exceptions for safe test fixtures and legitimate file operations, or they'll reject valid validator/test code itself. Pair each ban with specific intent (e.g., 'no raw_share_root reads except in fixtures at /mnt/local-analysis/raw-to-knowledge-playbook/tests/fixtures/').

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
