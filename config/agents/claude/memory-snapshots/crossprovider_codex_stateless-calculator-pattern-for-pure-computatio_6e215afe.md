---
name: crossprovider codex stateless-calculator-pattern-for-pure-computatio
description: Stateless calculator pattern for pure computations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [design-pattern, testing, pure-functions, statefulness]
---

Accept all parameters directly in each method rather than storing configuration in __init__. This makes dependencies explicit, simplifies testing, and prevents accidental shared state—useful for cost calculators, economics models, and other pure-function domains.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
