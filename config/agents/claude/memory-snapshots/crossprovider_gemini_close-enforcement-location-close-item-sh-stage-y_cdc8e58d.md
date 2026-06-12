---
name: crossprovider gemini close-enforcement-location-close-item-sh-stage-y
description: Close enforcement location: close-item.sh > stage YAML
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [workflow, enforcement, work-queue]
---

Stage YAML blocking_condition is informational only; exit_stage.py checks only artifact presence. For type:feature items, enforce feature-close-check.sh in close-item.sh itself (executable guard after Phase 2). Stage YAML documents this but doesn't enforce.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
