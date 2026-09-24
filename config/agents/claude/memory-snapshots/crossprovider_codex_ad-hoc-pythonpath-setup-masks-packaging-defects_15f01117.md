---
name: crossprovider codex ad-hoc-pythonpath-setup-masks-packaging-defects
description: Ad-hoc PYTHONPATH setup masks packaging defects
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pythonpath-hazard, packaging, cross-repo-testing]
---

Cross-repo test gates that wire PYTHONPATH manually instead of using install-based or `uv run` execution can hide import/packaging errors that would fail in real deployment environments. PYTHONPATH behavior also varies by shell/environment, creating false passes. Prefer explicit dependency installation over environment-variable path wiring.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
