---
name: plan-gated-issue-implementation
description: Workflow for executing pre-approved GitHub issues with mandatory validation checkpoints
version: 1.0.0
source: auto-extracted
extracted: 2026-04-11
metadata:
  tags: ["workflow", "github-issues", "validation", "documentation"]
---

# Plan-Gated Issue Implementation

For repos enforcing plan-approval gates, verify the issue has `status:plan-approved` before starting. Execute in parallel: (1) check for existing deliverables on disk, (2) read the issue comment history for prior context, (3) validate artifacts against source surfaces for accuracy and terminology. This prevents duplicate work and ensures implementation aligns with approved plans before creating new artifacts.