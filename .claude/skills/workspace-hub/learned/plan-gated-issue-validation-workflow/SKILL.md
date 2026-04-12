---
name: plan-gated-issue-validation-workflow
description: Systematic validation pattern for plan-approved GitHub issues with pre-existing deliverables
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["github-workflow", "validation", "plan-approval", "agent-teams"]
---

# Plan-Gated Issue Validation Workflow

For issues labeled `status:plan-approved`, validate deliverables in parallel phases: (1) check git status + read live issue + review approved plan, (2) verify deliverable files exist and read them, (3) validate files against requirements, (4) confirm auto-sync commit ancestry and diff state. This ensures pre-existing work meets spec before proceeding, avoiding redundant execution in agent-team runs.