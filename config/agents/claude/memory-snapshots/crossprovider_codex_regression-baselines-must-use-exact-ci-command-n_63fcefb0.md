---
name: crossprovider codex regression-baselines-must-use-exact-ci-command-n
description: Regression baselines must use exact CI command, not approximate local version
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, ci-gates, baseline-rigor]
---

Acceptance criteria claiming no regressions require a baseline from the exact CI command (including flags like `--maxfail=10`, `-p no:asyncio`, etc.). A local `pytest tests/` baseline cannot establish whether `pytest --maxfail=10 -p no:asyncio ...` will regress.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
