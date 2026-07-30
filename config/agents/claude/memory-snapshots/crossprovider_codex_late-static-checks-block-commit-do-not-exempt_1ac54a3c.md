---
name: crossprovider codex late-static-checks-block-commit-do-not-exempt
description: Late static checks block commit; do not exempt
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [quality-gates, refactoring, pre-commit]
---

Automated code size/complexity limits (e.g., 54 lines vs 50-line function maximum) caught by pre-completion cleanup audit should force refactor, not exemption or waiver. This is a safety checkpoint. Treat as UNEXPECTED residue and fix before commit amendment.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
