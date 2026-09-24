---
name: crossprovider codex malformed-git-metadata-test-matrix-catches-false
description: Malformed Git metadata test matrix catches false-green
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-testing, adversarial-testing, test-coverage]
---

Adversarial test coverage for corrupt `.git` layouts must include: symlinks, multiline/control metadata, missing/wrong-type common directory, forged/non-existent paths, wrong file types. These edge cases are non-obvious and produce false-green without explicit tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
