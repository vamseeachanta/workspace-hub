> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-10
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_repo_scope.md

---
name: Public repo scope
description: Only 4 public repos are development targets; OGManufacturing is client data only
type: feedback
---

Development happens in 4 public repos ONLY: digitalmodel, worldenergydata, assethold, assetutilities.
OGManufacturing is client data for confidentiality — NOT a development target.
Drilling and surveillance calculations belong in digitalmodel, not OGManufacturing.

**Why:** OGManufacturing contains client-specific data that must stay isolated. All reusable engineering work goes into the public repos.
**How to apply:** When scoping work, gap analysis, or calculations — only target the 4 public repos. Never suggest adding implementation code to OGManufacturing.
