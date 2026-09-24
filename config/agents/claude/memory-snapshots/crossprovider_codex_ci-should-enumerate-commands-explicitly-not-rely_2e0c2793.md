---
name: crossprovider codex ci-should-enumerate-commands-explicitly-not-rely
description: CI should enumerate commands explicitly, not rely on discovery
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ci, reproducibility, repo-local]
---

Keep CI workflows repo-local with explicit command enumeration (e.g., uv run python scripts/validate_*.py) rather than discovery patterns. Avoids external dependencies and makes coverage intentions visible in the workflow.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
