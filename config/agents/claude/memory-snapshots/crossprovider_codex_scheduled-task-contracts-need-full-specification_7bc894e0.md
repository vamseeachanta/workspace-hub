---
name: crossprovider codex scheduled-task-contracts-need-full-specification
description: Scheduled task contracts need full specification, not just cadence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [infrastructure, task-scheduling, specification]
---

Don't specify only schedule + command. Include task id, exact invocation (uv run, python, etc.), required capabilities/secrets, log path, error handling, retry policy, and parameter injection patterns. Incomplete contracts force implementation choices.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
