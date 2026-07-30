---
name: crossprovider codex explicit-config-paths-must-fail-nonzero-on-missi
description: Explicit config paths must fail nonzero on missing files
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [error-handling, discipline]
---

When a config path is explicitly specified (not implicitly discovered), a missing file should exit nonzero and block execution. Using `warn-skip` for *implicit* unprovisioned discovery is safe; explicit paths need fail-closed semantics.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
