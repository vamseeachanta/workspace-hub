---
name: crossprovider codex pickle-compatibility-breaks-across-module-path-r
description: Pickle compatibility breaks across module path refactors
metadata:
  type: reference
  source: codex
  bridged: 2026-07-30
  tags: [python-serialization, refactoring, backwards-compatibility, multiprocessing]
---

Changing module paths (e.g., app.services.X → digitalmodel.solvers.X) breaks deserialization of previously serialized objects and pickle-based multiprocessing communication, even when the code is importable. Existing joblib caches and rolling-version workers silently fail or load duplicate class instances with broken equality/isinstance checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
