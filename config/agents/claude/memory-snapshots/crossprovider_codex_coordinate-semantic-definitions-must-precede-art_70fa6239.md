---
name: crossprovider codex coordinate-semantic-definitions-must-precede-art
description: Coordinate-semantic definitions must precede artifact identity freezing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, planning, requirements, design]
---

Freezing a case/model hash before defining coordinate frames, sign conventions, and reference systems is architecturally broken; hash identity cannot be stable when semantics are still undefined. Define coordinate conventions and frame-binding rules in an earlier phase, not deferred to later work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
