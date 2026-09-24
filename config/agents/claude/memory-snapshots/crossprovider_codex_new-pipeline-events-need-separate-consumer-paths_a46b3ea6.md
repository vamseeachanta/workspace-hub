---
name: crossprovider codex new-pipeline-events-need-separate-consumer-paths
description: New pipeline events need separate consumer paths, not insertion into existing loops
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, codex-pattern, pipeline-safety, event-routing]
---

Patching a jq pipeline to emit new event types into the same stream that previously emitted only scalars (skill names) will corrupt downstream processing. Do not mix objects into a scalar stream. Define a separate handler path for new event types with an explicit target artifact or accumulator.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
