---
name: portable-baseline-configuration-pattern
description: Separate portable/universal config from machine-specific settings to enable safe template reuse across environments
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["configuration", "portability", "architecture", "multi-environment"]
---

# Portable Baseline Configuration Pattern

When managing configuration across multiple machines/environments, distinguish between portable baseline settings (safe on any system) and machine-specific wiring (hooks, plugins, paths). Store the portable baseline in a template file that can be version-controlled and reused, while keeping environment-specific configuration separate. Use canonical portable resolution patterns (e.g., `command -v python3 || command -v py`) rather than hardcoded paths or assumptions about tool availability.