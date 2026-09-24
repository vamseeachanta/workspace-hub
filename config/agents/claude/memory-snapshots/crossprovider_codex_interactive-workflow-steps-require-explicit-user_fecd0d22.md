---
name: crossprovider codex interactive-workflow-steps-require-explicit-user
description: Interactive workflow steps require explicit user handoff, not artifact-only drops
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [user-interaction-workflow, plan-validation, acceptance-criteria]
---

Stage 5 interactive planning is a collaborative user-agent session where scope, acceptance criteria, and risks are negotiated, not a one-way artifact publication. Agents that skip this treat plan creation as complete, leading to unvalidated assumptions and implementation drift. Interactive steps need separate evidence artifacts (e.g., user-review-common-draft.yaml) marking collaborative closure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
