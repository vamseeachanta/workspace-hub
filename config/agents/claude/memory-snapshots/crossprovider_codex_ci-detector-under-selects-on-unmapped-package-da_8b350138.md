---
name: crossprovider codex ci-detector-under-selects-on-unmapped-package-da
description: CI detector under-selects on unmapped package-data in digitalmodel
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [ci, digitalmodel, defect]
---

detect_touched_domains.py scoped_pyproject_domains() returns empty set for unknown package-data entries instead of falling back to full-matrix. This causes under-selection of required domain tests when pyproject.toml changes in unmapped ways.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
