---
name: crossprovider codex type-validation-must-explicitly-reject-booleans-
description: Type validation must explicitly reject booleans before numbers.Real
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [type-safety, edge-cases]
---

Python `bool` and NumPy `bool_` are technically `numbers.Real` but should fail numeric validation gates. Use explicit `isinstance(x, (bool, np.bool_))` rejection before testing `numbers.Real`, or invalid truthy values will pass (e.g., `correlation=True` becomes `1.0`).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
