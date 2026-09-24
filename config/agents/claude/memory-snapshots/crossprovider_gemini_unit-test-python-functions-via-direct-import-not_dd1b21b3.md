---
name: crossprovider gemini unit-test-python-functions-via-direct-import-not
description: Unit test Python functions via direct import, not subprocess
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, python, tdd]
---

Importing pure functions directly for unit testing is faster and more reliable than subprocess-based testing, which becomes integration testing. Reserve subprocess testing for CLI/cross-module interactions. WRK-1067 cross-review.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
