---
name: crossprovider codex test-coverage-claims-need-enumerated-cases-not-j
description: Test coverage claims need enumerated cases, not just counts
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, tdd, completeness]
---

Plans that claim 'deterministic coverage' or '≥5 tests' without listing cases mask shallow coverage. Enumerate: happy path, all error modes (missing/malformed input), boundary conditions, concurrency edge cases, and fallback paths. Shallow enumeration catches implementation defects that count-based claims miss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
