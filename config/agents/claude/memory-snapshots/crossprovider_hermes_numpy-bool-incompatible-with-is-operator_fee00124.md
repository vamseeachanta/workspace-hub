---
name: crossprovider hermes numpy-bool-incompatible-with-is-operator
description: numpy.bool_ incompatible with `is` operator
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [numpy, testing, type-checking, python-gotcha]
---

numpy.bool_(True) is not True — the identity check fails. Use == equality or assert-form comparisons instead: assert val (True) or assert not val (False), not assert val is True. This affects any test that naively compares numpy boolean return values.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
