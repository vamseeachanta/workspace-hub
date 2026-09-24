---
name: crossprovider codex shell-scripts-accepting-multiple-flags-should-va
description: Shell scripts accepting multiple flags should validate flag combinations early—not silently skip checks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell-scripting, argument-validation, test-coverage]
---

Accepting both `--ruff-only` and `--mypy-only` together, then running neither, is a false-green bug. Either reject conflicting flags during argument parsing or document which combinations are valid. Tests should verify that single-flag invocations actually run the intended checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
