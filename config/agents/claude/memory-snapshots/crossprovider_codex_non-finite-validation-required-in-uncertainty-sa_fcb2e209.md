---
name: crossprovider codex non-finite-validation-required-in-uncertainty-sa
description: Non-finite validation required in uncertainty/sampling code
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [validation, uncertainty, correctness, testing]
---

Plain `float` fields with standard Pydantic validators miss `nan` and `inf` inputs, allowing invalid prior parameters to produce NaN/inf samples downstream. Add explicit `finite_value` validators and test coverage with `.nan`/`.inf` YAML inputs for all numeric prior fields (bounds, mean, median, log parameters).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
