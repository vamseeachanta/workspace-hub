---
name: crossprovider codex licensed-solver-integration-uses-remote-executio
description: Licensed solver integration uses remote-execution pipeline
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [licensed-software, distributed-compute, workflow]
---

When a compute tool (OrcaFlex, ANSYS, etc.) requires a commercial license unavailable on the current host, split the workflow: local deterministic case generation → remote execution on licensed machine → results download and verification. Don't block on local license availability.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
