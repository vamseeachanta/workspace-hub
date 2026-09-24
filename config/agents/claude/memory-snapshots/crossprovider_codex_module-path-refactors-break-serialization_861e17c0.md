---
name: crossprovider codex module-path-refactors-break-serialization
description: Module path refactors break serialization
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [python, import, serialization, refactoring]
---

Pickle/joblib artifacts cannot deserialize when module identities change from relative paths to dotted imports. Class equality and isinstance() fail when multiple copies exist; mutable class state diverges between duplicates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
