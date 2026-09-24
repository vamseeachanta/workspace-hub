---
name: crossprovider codex documentation-updates-must-pair-with-runtime-beh
description: Documentation updates must pair with runtime behavior verification in acceptance criteria
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [runtime-parity, acceptance-criteria, quality-assurance]
---

Updating SKILL.md or docs alone does not guarantee runtime parity. When logic executes in shell runners or Python pipelines, acceptance criteria must explicitly cover updates to those execution paths, not just documentation drift.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
