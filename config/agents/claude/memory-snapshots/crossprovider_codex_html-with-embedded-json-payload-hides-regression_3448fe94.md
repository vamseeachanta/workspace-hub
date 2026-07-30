---
name: crossprovider codex html-with-embedded-json-payload-hides-regression
description: HTML with embedded JSON payload hides regressions
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [testing, html, json, regression-testing]
---

When testing rendered HTML with embedded JSON (e.g., report sidecars), assert visible region separately from full HTML. Full-document assertions miss visible regressions because payload strings remain even when the visual list stops rendering.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
