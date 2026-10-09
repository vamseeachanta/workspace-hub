---
name: multi-role-agent-contract-review-pipeline
description: Execute a 4-role agent team (Planner/Architect/Reviewer/Integrator) pipeline for self-reviewing knowledge artifacts before delivery
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["agent-orchestration", "contract-generation", "quality-assurance", "multi-step-execution"]
---

# Multi-Role Agent Contract Review Pipeline

When creating critical knowledge artifacts (contracts, specs) with no planned second human pass, structure execution as a 4-role pipeline: Planner grounds requirements, Architect drafts the artifact, Reviewer performs adversarial critique and flags gaps, Integrator applies revisions and adds cross-links. This self-review pattern catches inconsistencies early. Execute steps sequentially with role-switching, applying Reviewer recommendations before final Integrator pass.