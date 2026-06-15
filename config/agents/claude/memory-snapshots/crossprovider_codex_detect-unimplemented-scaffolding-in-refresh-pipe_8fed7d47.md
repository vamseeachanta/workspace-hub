---
name: crossprovider codex detect-unimplemented-scaffolding-in-refresh-pipe
description: Detect unimplemented scaffolding in refresh pipelines
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [architectural-audit, scaffolding-detection, pipeline-health]
---

Config files declaring enabled jobs do not guarantee implementation. Check for stubs by inspecting actual outputs: records_updated: 0, explicit return skipped, stale scheduler logs. This is critical when assessing refresh/ingest pipelines where staleness is a claimed feature.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
