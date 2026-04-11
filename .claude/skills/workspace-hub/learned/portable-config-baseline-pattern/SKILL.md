---
name: portable-config-baseline-pattern
description: Extract machine-agnostic settings into portable template files while keeping machine-specific hooks and plugins separate
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["architecture", "configuration-management", "portability"]
---

# Portable Config Baseline Pattern

When managing config files across multiple machines, separate portable baseline settings (safe everywhere) from machine-specific wiring (hooks, plugins, local paths). Use a template file (e.g., `config/agents/claude/settings.json`) as the canonical portable baseline, then layer machine-specific overrides in the live config. Verify separation by grepping for actual execution paths—only comments and diagnostic messages should reference machine-specific tools; all real calls use portable resolution patterns like `command -v python3 || command -v python`.