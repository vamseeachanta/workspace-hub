---
name: crossprovider codex optional-dependency-groups-don-t-auto-activate-i
description: Optional dependency groups don't auto-activate in uv
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [uv-python, plan-review, dependencies]
---

When a package (e.g., pytest-benchmark) is in `[dependency-groups].optional-dev`, `uv run` won't auto-activate it. Plan reviews should verify placement in `[dependency-groups].test` or other standard group, or add explicit activation logic. This affects multi-repo benchmark/test harness plans.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
