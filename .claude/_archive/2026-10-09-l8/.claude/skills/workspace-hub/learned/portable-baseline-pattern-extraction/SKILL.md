---
name: portable-baseline-pattern-extraction
description: Extract and separate portable baseline config from machine-specific overrides in multi-environment projects
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["configuration", "portability", "multi-environment", "architecture"]
---

# Portable Baseline Pattern Extraction

When managing config across multiple machines, separate portable baseline settings (safe on any system) from machine-specific wiring (hooks, plugins, paths). Read all target files in parallel to identify shared patterns, then use canonical resolution methods (e.g., `uv python find` or `command -v`) as the single source of truth. Wire machine-specific hooks sequentially into the template to avoid conflicts. Verify with grep to ensure no execution calls leak into portable templates.