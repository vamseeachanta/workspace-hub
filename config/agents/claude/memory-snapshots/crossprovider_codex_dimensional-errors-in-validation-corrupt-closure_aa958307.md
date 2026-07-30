---
name: crossprovider codex dimensional-errors-in-validation-corrupt-closure
description: Dimensional errors in validation corrupt closure signals
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [validation, testing, dimensional-analysis, closure-gates]
---

When validation includes derived quantities (e.g., mass = volume × density, GM = C44/mass), explicitly label all units and add regression tests for every assumption. Unlabeled or implicit dimensional conversions can lead to incorrect closure conclusions (e.g., claiming 93,383 tonnes when it's actually 93,383 m³).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
