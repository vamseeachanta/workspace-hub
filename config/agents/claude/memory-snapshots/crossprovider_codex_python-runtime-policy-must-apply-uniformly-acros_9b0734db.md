---
name: crossprovider codex python-runtime-policy-must-apply-uniformly-acros
description: Python runtime policy must apply uniformly across callsites
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [python-runtime, consistency, policy-enforcement]
---

Bare `python3` invocations from repo scripts should follow the workspace rule (uv run) throughout. Mixing bare python3 in new-feature.sh while other scripts use uv run creates portability failures on machines without python3. WRK-1130 required multiple rounds to flip all inline Python blocks to uv.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
