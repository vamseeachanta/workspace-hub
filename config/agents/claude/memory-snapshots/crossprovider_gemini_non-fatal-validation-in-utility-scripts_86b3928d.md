---
name: crossprovider gemini non-fatal-validation-in-utility-scripts
description: Non-fatal validation in utility scripts
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [shell-patterns, validation, error-handling]
---

Shell utility scripts (set-active-wrk.sh) warn about missing artifacts (e.g., WRK-*.md files) but continue execution; validation failures are logged to stderr but don't block the primary operation. Distinguish blocking vs advisory checks.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
