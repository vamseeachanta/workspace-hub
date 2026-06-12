---
name: crossprovider hermes iron-law-artifact-filtering-misses-derived-artif
description: Iron Law artifact filtering misses derived-artifact variants and may falsely treat user work as derived
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifact-filtering, data-loss-risk, disk-cleanup]
---

Standard cleanup filters (node_modules, .venv, __pycache__) miss platform-specific builds, .dist-info dir variations, build/, dist/, site-packages, .mypy_cache, and .ruff_cache (which contains user config, not just cache). Conversely, results/ subdirs may contain hand-edited analysis. A single rule cannot be safe; human review per bundle is load-bearing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
