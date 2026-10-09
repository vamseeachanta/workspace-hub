---
name: github-issue-structure-for-personal-finance-tracking
description: Pattern for organizing financial analysis work across multiple repos (data/config vs. logic separation)
version: 1.0.0
source: auto-extracted
extracted: 2026-04-13
metadata:
  tags: ["github-workflow", "financial-tracking", "repo-organization", "issue-design"]
---

# GitHub Issue Structure for Personal Finance Tracking

When building financial analysis systems, separate **confidential data/config** (private personal repo) from **algorithms/logic** (shared/public repo). Create the tracking issue in the data repo with clear references to algorithm repos where implementation lives. This enables sensitive portfolio info to stay private while keeping reusable code modular and potentially shareable. Flag browser access limitations early (e.g., Fidelity blocked by safety extensions) and establish manual data handoff workflows.