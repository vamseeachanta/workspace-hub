---
name: crossprovider hermes truthy-check-vs-boolean-validation-are-different
description: Truthy check vs boolean validation are different gates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, type-checking, test-coverage]
---

`if gate:` allows empty string, null, 0, False; `if isinstance(gate, bool) and gate:` requires true boolean. Shallow validators pass truthy; full gates fail on non-bool. Acceptance-critical fields require explicit boolean validation, not truthiness. Tests must cover both null and string-false cases.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
