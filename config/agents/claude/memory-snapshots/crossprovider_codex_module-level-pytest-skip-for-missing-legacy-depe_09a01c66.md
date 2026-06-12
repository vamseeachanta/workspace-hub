---
name: crossprovider codex module-level-pytest-skip-for-missing-legacy-depe
description: Module-level pytest skip for missing legacy dependencies
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [pytest, testing, legacy-code, dependencies]
---

Use `@pytest.mark.skipif(not IMPORT_AVAILABLE, reason='...')` at module scope to skip entire legacy test files when their imports fail or dependencies are absent. This is safer than collection-time exceptions and signals intent.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
