---
name: crossprovider hermes namespace-package-imports-fail-silently-when-sha
description: Namespace package imports fail silently when shadowed by installed package
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [python-imports, namespace-packages, sys-path-hazard]
---

Scripts directory without `__init__.py` allows repo-relative imports only if repo root is in sys.path AND no external installed package with same name shadows the namespace. Failures are silent or produce confusing ModuleNotFoundError; fallback to `importlib.util.spec_from_file_location` + `exec_module` is more robust than sys.path manipulation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
