---
name: crossprovider hermes pytest-importorskip-skips-entire-module-when-opt
description: pytest.importorskip skips entire module when optional dep missing — correct pattern for matplotlib/plotly
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [pytest, optional-dependencies]
---

Using `pytest.importorskip('matplotlib')` at module level skips all tests in that file (not just matplotlib-dependent ones) when the dependency is missing. This is appropriate for packages like field_development that require matplotlib for all functionality. No test failure, no regression — just skip.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
