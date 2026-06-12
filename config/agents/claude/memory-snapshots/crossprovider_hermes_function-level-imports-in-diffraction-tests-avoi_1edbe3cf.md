---
name: crossprovider hermes function-level-imports-in-diffraction-tests-avoi
description: Function-level imports in diffraction tests avoid import-chain hang from __init__.py → aqwa_converter → loguru
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [test-patterns, import-hang, mock-strategy]
---

Diffraction test conftest uses function-level imports (import module inside test function, not at top) to avoid pulling aqwa_converter at suite startup, which imports loguru and causes 30+ second hangs. Pattern: pass conftest fixtures that supply mocks instead of importing converter modules directly.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
