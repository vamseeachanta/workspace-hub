---
name: crossprovider codex docs-ci-skips-generator-only-regressions
description: Docs CI skips generator-only regressions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ci-gap, regression-detection, generated-content]
---

Docs freshness CI job (`check_generated_html.py`) is triggered only by committed HTML changes, not by `scripts/**/build_*.py` or generator modifications. Generator-only regressions bypass detection. CI should trigger on both generator script changes and the checker script itself, placed after uv installation and before brand guard.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
