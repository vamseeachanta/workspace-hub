---
name: crossprovider gemini timeout-readiness-layering-distinguishes-missing
description: Timeout + readiness layering distinguishes missing from broken
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [error-handling, timeouts, health-checks]
---

Separate checks: `command -v tool` (existence) vs `tool --test-op` (functionality). Use configurable timeout wrapper (read from YAML config, default 30s) around blocking ops. Distinguish exit codes: 2 for missing, 124 for timeout, 0 for pass. Prevents hangs that look like network outages.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
