---
name: crossprovider codex grep-based-audit-heuristics-produce-false-positi
description: Grep-based audit heuristics produce false positives on real corpus
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [auditing, false-positives, skill-coverage, WRK-1053]
---

WRK-1053 skill-coverage-audit only detects `bash scripts/`, `uv run`, or frontmatter `scripts:` but misses valid patterns like `./scripts/...`, `python3 scripts/...`, backticks, and relative paths already used in 508-skill library. Audit reports true positives as gaps, creating noise. Heuristics must validate against actual corpus patterns before deployment.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
