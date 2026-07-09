---
name: crossprovider codex approval-ready-requires-local-markers-plus-revie
description: Approval-ready requires local markers plus review artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-07-05
  tags: [approval, workflow, gates]
---

Approval gate needs both GitHub status:plan-approved label AND local .planning/plan-approved/<issue>.md marker AND scripts/review/results/*plan-NNN* review artifacts. Local markers are human-explicit gate; labels alone insufficient.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
