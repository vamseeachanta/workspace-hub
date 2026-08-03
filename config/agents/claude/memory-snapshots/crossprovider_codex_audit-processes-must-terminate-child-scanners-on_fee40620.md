---
name: crossprovider codex audit-processes-must-terminate-child-scanners-on
description: Audit processes must terminate child scanners on interruption
metadata:
  type: reference
  source: codex
  bridged: 2026-07-20
  tags: [process-hygiene, audit-practices, i-o-discipline]
---

Interrupted agents and read-only audit tasks can leave scanner processes running in the background, driving sustained I/O pressure. Require explicit cleanup of task-owned processes (e.g., find, rg, ps scans) when agents are interrupted or completed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
