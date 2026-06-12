---
name: crossprovider gemini external-expected-failure-lists-become-unmaintai
description: External expected-failure lists become unmaintainable with parameterized tests
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [testing, pytest, maintainability, parameterization]
---

WRK-1054: Managing expected failures via external text file (e.g., expected-failures.txt with exact node IDs) is fragile when test parameters change node ID string representations. Use pytest's native `@pytest.mark.xfail` decorators in test code instead.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
