---
name: crossprovider codex acceptance-gates-must-be-owned-upstream-not-down
description: Acceptance gates must be owned upstream, not downstream in roadmap dependencies
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [roadmap, dependencies, architecture]
---

Roadmap issues with acceptance gates requiring downstream evidence serialize parallel work unnecessarily. Structure dependencies so gate ownership stays upstream of implementation lanes; separate private/public boundaries from gate ownership.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
