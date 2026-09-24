---
name: crossprovider gemini test-mocking-for-import-errors-via-sys-modules
description: Test mocking for import errors via sys.modules
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, mocking, imports, test-patterns]
---

Use `patch.dict(sys.modules, {"module_name": None})` to simulate a missing import during tests. Cleaner than manipulating sys.path or attempting to uninstall packages mid-test, and validates that fail-closed guards work as expected.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
