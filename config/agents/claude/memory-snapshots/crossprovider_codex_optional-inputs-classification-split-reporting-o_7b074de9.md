---
name: crossprovider codex optional-inputs-classification-split-reporting-o
description: Optional inputs classification: split reporting-only from coverage-affecting
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-integrity, optional-inputs, gap-detection]
---

Plans must distinguish optional inputs that affect correctness (e.g., join-corpus records) from those that affect reporting only. Missing coverage-affecting inputs silently shrink the source universe and under-report gaps, but can exit 0 if not explicitly fail-closed. Plan must specify fail-closed or degraded-run behavior for each coverage-affecting optional input.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
