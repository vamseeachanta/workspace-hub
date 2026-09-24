---
name: crossprovider codex bandit-use-native-baseline-b-instead-of-custom-m
description: Bandit: use native baseline (-b) instead of custom matching
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, static-analysis, tool-config]
---

Native `bandit -b baseline.json` handles finding suppression correctly; avoid reimplementing the matching key with custom logic. Accept tool limitations (e.g., line drift after refactors) and document a refresh strategy rather than building custom comparison code.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
