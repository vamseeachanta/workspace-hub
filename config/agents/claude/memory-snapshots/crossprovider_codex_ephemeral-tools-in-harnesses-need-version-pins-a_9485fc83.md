---
name: crossprovider codex ephemeral-tools-in-harnesses-need-version-pins-a
description: Ephemeral tools in harnesses need version pins and error contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [harness, tool-versioning, reproducibility, bash]
---

Tools embedded in repeated harness scripts (pip-audit, formatters, linters) must have explicit version pins and documented error-handling contracts. Use `uv run --with tool==X.Y.Z` and document what each exit code means, when output is non-parseable, and how to recover. Tool drift breaks weekly/cron reproducibility.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
