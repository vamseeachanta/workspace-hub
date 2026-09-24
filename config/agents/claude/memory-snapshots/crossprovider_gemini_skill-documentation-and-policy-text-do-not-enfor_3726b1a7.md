---
name: crossprovider gemini skill-documentation-and-policy-text-do-not-enfor
description: Skill documentation and policy text do not enforce behavior without executable backing
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workflow, automation, tooling]
---

Discrepancy between documented workflow (in skill .md files) and implemented workflow (in executable scripts) is endemic. Gates described in policy text must be mirrored in the actual entry-point scripts (e.g., `scripts/agents/plan.sh`) with identical logic, otherwise documented gates become advisory only.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
