---
name: crossprovider gemini fast-pre-check-before-pytest-collection-saves-15
description: Fast pre-check before pytest collection saves 15-30s per repo
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [test-performance, pytest-optimization, ci-efficiency]
---

Grep for pytest.mark.smoke markers before running pytest; skip collection entirely if no tests exist. Collections alone take 13-15s per repo in large monorepos. Pre-check pattern: `grep -rl '@pytest.mark.smoke' tests/ && pytest -m smoke` vs bare `pytest -m smoke`. Saves 30s+ in nightly test runs across tier-1 repos.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
