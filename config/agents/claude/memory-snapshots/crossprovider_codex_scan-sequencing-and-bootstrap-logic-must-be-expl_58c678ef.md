---
name: crossprovider codex scan-sequencing-and-bootstrap-logic-must-be-expl
description: Scan sequencing and bootstrap logic must be explicit to avoid deadlocks and self-reference
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scan-sequencing, compliance-bootstrap, process-ordering]
---

When processes create artifacts that must later pass compliance scanning, the scan-ordering, bootstrap rules (e.g., excluding self-referential artifacts from compliance input), and timing relative to commits must be explicit. Undefined sequencing creates circular waits—e.g., manifest must list its own hash (impossible) or remain incomplete.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
