---
name: crossprovider codex migration-tooling-must-fail-closed-on-validation
description: Migration tooling must fail-closed on validation gaps
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [migration-safety, validation, tooling]
---

Malformed or missing config (empty remap lists, misspelled YAML keys, invalid domain labels) silently succeed as no-ops in current migration tools. Reviewed migrations should validate input strictness and reject incomplete batches before `--apply` proceeds.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
