---
name: crossprovider codex import-path-divergence-after-refactoring-breaks-
description: Import path divergence after refactoring breaks downstream tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [refactoring, test-maintenance]
---

When refactoring moves code from `modules.bsee.analysis.production_api12` to `bsee.analysis.production_api12`, test files retaining old import paths either fail outright or (if wrapped in try/except ImportError) silently collect but fail at runtime. Import path updates must sweep all consuming test files.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
