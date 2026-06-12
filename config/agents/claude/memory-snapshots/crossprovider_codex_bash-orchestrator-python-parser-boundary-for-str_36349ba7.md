---
name: crossprovider codex bash-orchestrator-python-parser-boundary-for-str
description: Bash orchestrator + Python parser boundary for structured data
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [bash, testing, parser-design]
---

When bash scripts need to parse machine-readable output (pytest, JSON, YAML), delegate parsing to Python via `uv run` to avoid brittle regex and shell quoting bugs. Validated by three separate pytest node-ID parsing regressions where regex truncated parameterized IDs containing embedded separators; a Python parser with structured output handling would have caught this immediately.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
