---
name: crossprovider codex fail-closed-yaml-validation-beats-silent-skip-in
description: Fail-closed YAML validation beats silent skip in shell
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell-safety, yaml-validation, fail-closed]
---

When shell scripts conditionally run python3 or uv for YAML validation, prefer `return 1` + ERROR message over WARN + silent continuation. The pattern: abstract to a `run_config_python` helper that tries python3, then uv, then fails closed. Silently skipping validation creates deployment-time surprises.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
