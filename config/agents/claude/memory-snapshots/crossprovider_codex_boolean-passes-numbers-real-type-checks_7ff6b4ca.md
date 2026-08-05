---
name: crossprovider codex boolean-passes-numbers-real-type-checks
description: Boolean passes `numbers.Real` type checks
metadata:
  type: reference
  source: codex
  bridged: 2026-08-04
  tags: [type-validation, python-quirks, test-coverage]
---

Python and NumPy bool are instances of `numbers.Real`; validators using `isinstance(x, numbers.Real)` accept True/False as numeric values. Numeric validation must explicitly exclude bool/np.bool_ before the Real check.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
