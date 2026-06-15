---
name: crossprovider codex cron-uv-resolution-needs-explicit-validation-and
description: Cron uv resolution needs explicit validation and fallback chains
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [uv, ci, script-hardening]
---

Direct-caller scripts (like skill validation) should support `UV_BIN` override, validate `uv --version`, provide common-path fallback (e.g. `$HOME/.local/bin/uv` → `/usr/bin/uv`), and emit actionable diagnostics on failure. CI should filter on resolver script changes and test the resolution logic directly via dedicated test suite (e.g. `test_skill_validation_uv_resolution.py`).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
