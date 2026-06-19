---
name: crossprovider codex python-bool-int-type-coercion-in-validators-acce
description: Python bool/int type coercion in validators accepts malformed input
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [type-safety, schema-validation, python-gotchas]
---

Validators using `isinstance(value, int)` pass JSON booleans (Python `bool` is an int subclass), allowing `True`/`False` to pass numeric field validation. Affects #730 and #733 overlap/ratio fields. Requires explicit `type(x) is int` checks or stricter union patterns to reject bool.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
