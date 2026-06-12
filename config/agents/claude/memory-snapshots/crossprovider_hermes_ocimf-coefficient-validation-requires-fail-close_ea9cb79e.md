---
name: crossprovider hermes ocimf-coefficient-validation-requires-fail-close
description: OCIMF coefficient validation requires fail-closed semantic gate, not regex
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [ocimf, test-gates, naval-architecture]
---

Simple regex matching for `ocimf_cy = heading_sin` fails to catch variants like `ocimf_cy = 1.0 * heading_sin`. Tests must either parse formulas to verify workbook-backed provenance or fail if any inline coefficient literal is detected. #2760 constraint: coefficients must source from licensed off-repo workbook or fail closed.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
