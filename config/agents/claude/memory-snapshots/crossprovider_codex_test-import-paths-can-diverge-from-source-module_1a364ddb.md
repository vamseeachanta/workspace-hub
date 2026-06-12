---
name: crossprovider codex test-import-paths-can-diverge-from-source-module
description: Test import paths can diverge from source module structure
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [refactoring, imports, test-maintenance]
---

Legacy or refactored test fixtures may import from paths that no longer exist in the source tree (e.g., `worldenergydata.modules.bsee.analysis.production_api12` when the real path is `worldenergydata.bsee.analysis.production_api12` without `.modules`). try/except ImportError masks these; audit refactors to update test imports.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
