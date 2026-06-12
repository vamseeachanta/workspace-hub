---
name: crossprovider hermes stale-pyc-files-can-mask-legitimate-import-addit
description: stale .pyc files can mask legitimate import additions
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [python-debugging, import-errors, bytecode-cache]
---

Import errors like 'cannot import name X from utils' can persist after code adds the symbol due to stale `.pyc` files in `__pycache__/`. Clear bytecode cache via `find . -path '*/__pycache__/*' -delete` and rerun. Python's timestamp-based invalidation may not trigger with skewed timestamps or stale long-running processes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
