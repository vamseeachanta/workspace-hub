---
name: crossprovider codex idempotency-contracts-must-exclude-files-with-em
description: Idempotency contracts must exclude files with embedded timestamps
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [idempotency, config-design]
---

Plans claiming idempotent re-runs must specify which files are permitted to change (timestamps, caches, state files). Rewriting config files due to embedded timestamps violates idempotency semantics and breaks downstream automation that assumes no-change behavior on safe re-runs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
