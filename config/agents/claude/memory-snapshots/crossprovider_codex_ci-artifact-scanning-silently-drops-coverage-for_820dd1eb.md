---
name: crossprovider codex ci-artifact-scanning-silently-drops-coverage-for
description: CI artifact scanning silently drops coverage for missing paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ci-design, coverage-gap, fail-open]
---

Validators configured to scan public artifacts skip paths that don't exist locally without failing, silently removing those files from coverage. A missing or untracked file drops out of CI checks instead of causing an explicit failure. Require pre-validation or explicit failure on missing scan paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
