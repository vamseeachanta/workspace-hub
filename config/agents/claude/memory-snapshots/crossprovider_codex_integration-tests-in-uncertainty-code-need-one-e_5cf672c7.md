---
name: crossprovider codex integration-tests-in-uncertainty-code-need-one-e
description: Integration tests in uncertainty code need one end-to-end run_matrix → analytics chain
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [testing, tdd, uncertainty, integration-tests]
---

TDD coverage with synthetic input frames (e.g., `_run_df()` handbuilt) misses bugs in the YAML-to-sample-to-analytics pipeline. Add at least one test that calls `run_matrix` once, then runs all analytics functions (tornado, spearman, percentile, fan) from that single result frame.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
