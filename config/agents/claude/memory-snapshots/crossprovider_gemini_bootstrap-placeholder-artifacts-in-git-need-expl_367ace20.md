---
name: crossprovider gemini bootstrap-placeholder-artifacts-in-git-need-expl
description: Bootstrap/placeholder artifacts in git need explicit replacement before closure
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [artifacts, testing, closure, windows-parity]
---

YAML/config placeholders (e.g., `.claude/state/harness-readiness-*.yaml` marked as bootstrap) created during repo-side setup must be replaced with real execution evidence before closing the issue. Placeholder artifacts left in repo create false confidence in readiness/parity and undermine trust in status reporting.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
