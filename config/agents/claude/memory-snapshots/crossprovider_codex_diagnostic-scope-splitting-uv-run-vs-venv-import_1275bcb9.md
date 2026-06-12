---
name: crossprovider codex diagnostic-scope-splitting-uv-run-vs-venv-import
description: Diagnostic scope splitting: uv run vs .venv import latency are independent faults
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [diagnostics, timeout-isolation, uv-run, scope-splitting]
---

When debugging slow CLI startup, uv run timeout (environment resolution, lock, metadata, cache) and .venv import latency (pandas, module-specific clients) are separate failure modes. Evidence: `.venv/bin/python -c print()` ≤0.1s but `uv run python -c print()` times out; must classify uv as host/environment state vs. repo-code defect before proposing fixes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
