---
name: crossprovider codex duplicated-governance-surface-path-lists-can-dri
description: Duplicated governance surface path lists can drift apart over time
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [config-management, governance, single-source-of-truth]
---

When `.github/workflows/` hardcodes scan path lists and Python code separately maintains `public_scan_paths()`, they diverge: workflow lags behind code, or vice versa. Store path lists in a single source of truth (e.g., YAML config) and read from it in both CI and code. Verify CI path list against Python path list in smoke tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
