---
name: crossprovider codex test-executable-mode-assumptions-break-on-sparse
description: Test executable-mode assumptions break on sparse checkouts
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [testing, test-hermiticity, sparse-checkout]
---

Tests that gate on tracked `+x` permissions will report false-pass (skip) because sparse checkout may not preserve mode bits. Force-run such tests to discover live dependencies (GitHub API calls, cloned state) that are NOT hermetic. Baseline must be real behavior, not issue description.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
