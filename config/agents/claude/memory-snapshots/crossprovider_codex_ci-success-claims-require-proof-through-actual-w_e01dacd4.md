---
name: crossprovider codex ci-success-claims-require-proof-through-actual-w
description: CI success claims require proof through actual workflow paths, not local testing inference
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, ci-verification, test-strategy]
---

Plans claiming first-run CI green must verify the workflow can succeed by showing all dependencies exist (e.g., coverage.json for quality gates). Local test commands that differ from CI commands need explicit justified deviation; regression baselines must capture the full suite being compared, not just partial collection. See #2441 where CI Quality Gates would fail due to missing coverage.json and test baseline was insufficient.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
