---
name: portable-baseline-pattern-implementation
description: Implement portable configuration baselines by separating machine-agnostic settings from machine-specific hooks and plugins
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["architecture", "configuration", "portability", "hardening"]
---

# Portable Baseline Pattern Implementation

When hardening cross-platform configs, separate portable baseline settings (safe on any machine) from machine-specific wiring (hooks, plugins, marketplace config). Read all context files and target files in parallel first. Use existing repo patterns (e.g., `uv python find` for Python resolution) as canonical references. Verify changes don't introduce hardcoded execution paths—check grep results for actual execution calls vs. safe fallback probes. Implement sequential edits to shared files, then run verification suite (git diff, status, targeted greps).