---
name: crossprovider hermes lazy-imports-require-source-location-mocking-in-
description: Lazy imports require source-location mocking in pytest
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [pytest, mocking, lazy-imports, patch-target]
---

For functions with lazy imports inside the function body (not module-level), patch() must target the import source location, not the importing module. Example: if run_foo() has 'from bar import Cls' inside, patch('bar.Cls') works but patch('run_module.Cls') fails because Cls isn't a module attribute until the function runs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
