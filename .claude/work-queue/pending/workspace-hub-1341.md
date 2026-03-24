---
id: workspace-hub#1341
title: "slim down large repos — relocate PDFs, reduce .git bloat"
status: pending
priority: high
complexity: complex
created_at: 2026-03-24T09:14:36Z
parent:
target_repos:
  - workspace-hub
  - digitalmodel
  - aceengineer-website
commit:
spec_ref:
related: []
blocked_by: []
synced_to: []
plan_reviewed: false
plan_approved: false
percent_complete: 0
computer: ace-linux-2
execution_workstations: [dev-primary, dev-secondary]
plan_workstations: [dev-primary]
provider: claude
provider_alt:
stage_evidence_ref: .claude/work-queue/assets/WRK-1341/evidence/stage-evidence.yaml
subcategory: operations
category: infrastructure
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1341
---
# Slim Down Large Repos — Relocate PDFs, Reduce .git Bloat

## Mission
Large repos are causing slow sync times. Three-pronged approach:
1. Remove PDFs from repos and relocate to mounted document-intelligence volume (related WRK exists)
2. Investigate saving large .git folders to a separate branch or using shallow clones (emergency measure)
3. Make all existing repos lean going forward — enforce size limits, add .gitattributes LFS rules or exclusions

## Context
- Sync times are unacceptably long on some machines
- PDFs should live in document-intelligence mount, not in git
- .git folder bloat is the primary culprit for slow clones/fetches

## Acceptance Criteria
- [ ] Audit all repos for large files (PDFs, binaries) with size report
- [ ] Remove PDFs from git history (git filter-repo or BFG) and relocate to document-intelligence mount
- [ ] Evaluate orphan-branch approach for preserving .git history without bloating clones
- [ ] Implement shallow clone or partial clone strategy for daily use
- [ ] Add .gitattributes / pre-commit hooks to prevent large binary re-introduction
- [ ] Verify sync times improve on all machines
- [ ] Document the new policy for binary/PDF files
