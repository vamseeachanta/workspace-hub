---
name: crossprovider codex multi-repo-quality-test-orchestrators-must-handl
description: Multi-repo quality/test orchestrators must handle per-repo tooling variance—no assumptions about uniform dependency sets
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [multi-repo, tooling, robustness]
---

Scripts that run checks on multiple repos (e.g., `mypy` on tier-1) cannot assume all repos declare the same tools in pyproject.toml. Per-repo fallback behavior must be explicit and tested, or the script will mysteriously fail for repos that lack the tool without clear error reporting.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
