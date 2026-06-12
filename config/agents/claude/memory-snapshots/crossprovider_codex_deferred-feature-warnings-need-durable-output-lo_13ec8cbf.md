---
name: crossprovider codex deferred-feature-warnings-need-durable-output-lo
description: Deferred feature warnings need durable output location
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [warnings, artifact-design, durability]
---

#609 defers body-level control-surface validation to upstream but provides no place in the run artifact or manifest to store deferred-feature warnings. Without durable storage, warnings are silently lost at EOF.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
