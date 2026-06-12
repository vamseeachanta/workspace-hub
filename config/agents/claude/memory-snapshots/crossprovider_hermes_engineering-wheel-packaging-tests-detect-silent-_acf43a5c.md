---
name: crossprovider hermes engineering-wheel-packaging-tests-detect-silent-
description: Engineering wheel packaging tests detect silent resource loss
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, wheel-build, package-data, ci]
---

Wheel-building tests (e.g. checking fixture file presence in built distributions vs. source tree) catch packaging regressions that local-source tests miss. Recommend always building a test wheel and inspecting contents before merging packaging changes, especially when modifying pyproject.toml package-data patterns.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
