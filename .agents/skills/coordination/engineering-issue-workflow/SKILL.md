---
name: engineering-issue-workflow
description: Engineering-specific discovery, qualification, implementation and verification
  for calculation, standards, solver and data-pipeline issues. Generic planning and
  authority follow the shared lifecycle.
metadata:
  category: coordination
  triggers:
  - When a GitHub issue with cat:engineering, cat:engineering-calculations, cat:engineering-methodology,
    or cat:data-pipeline is mentioned or assigned
  - When the user asks to implement any engineering calculation, offshore standard,
    metocean, OrcaFlex, or data-pipeline work
  - When any commit touches digitalmodel/, worldenergydata/, or assetutilities/
  version: 1.3.0
---

# Canonical skill adapter

Read and follow the [canonical skill](../../../../.claude/skills/coordination/engineering-issue-workflow/SKILL.md) before acting.
Resolve its relative references from the canonical skill directory and repository
paths from the explicitly identified workspace-hub checkout.

If the canonical source is unavailable, report that gap and stop this skill; do not
substitute a stale provider copy. This adapter adds no authority or installation.
