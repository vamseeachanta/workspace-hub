---
name: portable-baseline-config-pattern
description: Separate machine-portable baseline config from environment-specific hooks and plugins
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["configuration", "portability", "architecture", "templates"]
---

# Portable Baseline Config Pattern

When expanding configuration templates, partition settings into portable baseline (safe on any machine) vs. environment-specific (hooks, plugins, marketplace config). Use canonical tool resolution patterns like `uv python find` or `command -v` fallbacks already established in the codebase. Implement multi-package changes targeting the same file sequentially to avoid merge conflicts. Verify actual execution calls are replaced and only comments/diagnostics remain.