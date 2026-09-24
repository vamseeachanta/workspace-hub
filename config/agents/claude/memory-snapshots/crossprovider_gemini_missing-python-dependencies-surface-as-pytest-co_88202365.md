---
name: crossprovider gemini missing-python-dependencies-surface-as-pytest-co
description: Missing Python dependencies surface as pytest collection failures, not test failures
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, python, ci, debugging]
---

A missing import (e.g., `from pylife import ...`) produces "pytest collection failed" errors before any test runs, making root-cause less obvious than actual test failures. Early CI smoke-test for package imports (`import module_name`) catches these faster and with clearer signal than waiting for full pytest collection.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
