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

Current authority: implementation follows the originating task request or established standing authority after proportionate planning, TDD and adversarial review; no separate plan approval, approval label or local marker is required. Planning-only limits, unresolved domain decisions and action-specific authorization for publication, deployment, access changes, destructive actions and outreach remain binding. Historical approval records stay intact and must not be fabricated or self-labeled.


For repos enforcing plan-approval gates, verify current task authority and reviewed scope before starting; a separate approval label is not required. Execute in parallel: (1) check for existing deliverables on disk, (2) read the issue comment history for prior context, (3) validate artifacts against source surfaces for accuracy and terminology. This prevents duplicate work and ensures implementation aligns with approved plans before creating new artifacts.