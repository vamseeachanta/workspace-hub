---
name: crossprovider codex nan-inf-floats-pass-numeric-validation-but-break
description: NaN/inf floats pass numeric validation but break downstream serialization
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-safety, json-serialization, numeric-validation]
---

`json.loads` can produce NaN/inf floats; validation with `value <= 0` does not reject them; downstream `json.dumps(..., allow_nan=False)` then fails. Add explicit finite-number validation (`math.isfinite()` check) before formatting/serialization, not just range checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
