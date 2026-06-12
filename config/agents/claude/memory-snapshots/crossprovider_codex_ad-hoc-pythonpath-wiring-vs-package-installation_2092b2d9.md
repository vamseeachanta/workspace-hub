---
name: crossprovider codex ad-hoc-pythonpath-wiring-vs-package-installation
description: Ad-hoc PYTHONPATH wiring vs. package installation in cross-repo tests
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [python-dependencies, cross-repo-testing]
---

Setting `PYTHONPATH` to overlay uninstalled repos can mask packaging/export defects and create false passes that don't reproduce with real imports. Cross-repo gates should use `uv run --project <repo>` or install-based execution so tests exercise the actual import surface.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
