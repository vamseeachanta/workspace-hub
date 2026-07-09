---
name: crossprovider codex test-module-imports-of-hyphenated-packages-regis
description: Test module imports of hyphenated packages: register sys.modules on import
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [testing, python]
---

When tests import hyphenated package names (e.g., `scripts.data.drive-index.search`), Python's import machinery requires manual registration in `sys.modules` before dataclass/dynamic module loads succeed. Use conftest.py fixtures to register the hyphenated path before test collection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
