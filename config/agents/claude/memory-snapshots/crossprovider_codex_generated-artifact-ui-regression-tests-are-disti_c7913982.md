---
name: crossprovider codex generated-artifact-ui-regression-tests-are-disti
description: Generated artifact UI regression tests are distinct from numerical validation
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, artifacts, regression]
---

Plotly/HTML chart regressions (duplicate traces, axis label mismatches, signed vs unsigned extrema) can coexist with green numerical tests. Focused unit tests for calculation pipelines don't catch artifact rendering drift. Regression suite should validate generated output text/structure separate from correctness of the underlying data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
