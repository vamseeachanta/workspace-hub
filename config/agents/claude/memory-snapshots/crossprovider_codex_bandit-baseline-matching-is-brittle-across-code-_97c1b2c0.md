---
name: crossprovider codex bandit-baseline-matching-is-brittle-across-code-
description: Bandit baseline matching is brittle across code refactors
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [bandit, baseline-gating, static-analysis]
---

Baselines keyed by (test_id, file, line_number) re-flag existing findings as new after code edits above them shift line numbers. Use Bandit's native `-b` baseline matching only, not custom comparison logic; accept line-drift as a documented limitation with a refresh command for major refactors.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
