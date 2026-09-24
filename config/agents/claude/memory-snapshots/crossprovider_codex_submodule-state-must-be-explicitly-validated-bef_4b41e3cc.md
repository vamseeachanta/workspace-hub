---
name: crossprovider codex submodule-state-must-be-explicitly-validated-bef
description: Submodule state must be explicitly validated before large migrations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-operations, submodules, prerequisite-validation]
---

Add `git submodule sync --recursive` and `git submodule update --init --recursive` to migration prerequisites, not as side steps. Partial or stale submodule state silently causes path mapping and integrity failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
