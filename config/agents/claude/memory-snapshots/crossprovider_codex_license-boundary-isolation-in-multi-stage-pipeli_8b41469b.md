---
name: crossprovider codex license-boundary-isolation-in-multi-stage-pipeli
description: License boundary isolation in multi-stage pipelines
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [licensing, boundary-design, pipeline-architecture, gate-pattern]
---

When a pipeline stage requires licensing (e.g., OrcFxAPI), isolate it to a single licensed host. Define the boundary explicitly: only that host imports and executes the licensed code; all other pipeline stages run license-free without touching the licensed library. Write separate tests for licensed vs. non-licensed execution paths and ensure non-licensed machines fail with clear messaging if they cross the boundary.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
