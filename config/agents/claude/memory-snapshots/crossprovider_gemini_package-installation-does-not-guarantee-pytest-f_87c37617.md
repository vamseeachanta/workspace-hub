---
name: crossprovider gemini package-installation-does-not-guarantee-pytest-f
description: Package installation does not guarantee pytest fixture availability
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [pytest, plugins, diagnosis]
---

pytest_benchmark can be successfully imported from the venv but pytest still reports `fixture 'benchmark' not found`. This distinction matters: local env inspection and CI workflow validation must be done separately — package presence ≠ fixture registration.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
