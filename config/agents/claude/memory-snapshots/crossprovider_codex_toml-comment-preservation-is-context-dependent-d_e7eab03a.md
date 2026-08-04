---
name: crossprovider codex toml-comment-preservation-is-context-dependent-d
description: TOML comment preservation is context-dependent during merges
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [toml, comments, merging, test-coverage]
---

Owned-key trailing comments are discarded during TOML merges; only comments attached to unowned keys are preserved. Multiline and inline-table comments have separate handling paths and require explicit coverage in test fixtures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
