---
name: crossprovider codex verification-procedures-must-specify-exact-execu
description: Verification procedures must specify exact executable commands
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [procedures, verification, automation, specification]
---

Specifications and plans requiring verification must name exact commands (e.g., `uv run scripts/cron/validate-schedule.py`), not vague descriptions (e.g., 'schedule validation'). Vague commands cannot be executed, verified, or automated. All procedural steps must be concrete shell invocations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
