---
name: writing-plans
description: Turn a scoped objective into an implementation plan with affected files,
  dependencies, acceptance criteria and verification. Use the canonical issue template
  and shared lifecycle authority.
license: MIT
metadata:
  version: 1.3.0
  author: Hermes Agent (adapted from obra/superpowers)
  hermes:
    tags:
    - planning
    - design
    - implementation
    - workflow
    - documentation
    related_skills:
    - subagent-driven-development
    - test-driven-development
    - requesting-code-review
---

# Canonical skill adapter

Read and follow the [canonical skill](../../../../../.claude/skills/development/planning/writing-plans/SKILL.md) before acting.
Resolve its relative references from the canonical skill directory and repository
paths from the explicitly identified workspace-hub checkout.

If the canonical source is unavailable, report that gap and stop this skill; do not
substitute a stale provider copy. This adapter adds no authority or installation.
