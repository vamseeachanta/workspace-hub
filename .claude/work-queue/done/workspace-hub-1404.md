---
id: WRK-1404
title: "Organize /mnt/ace/docs/ subfolders and deduplicate engineering references"
repo: workspace-hub
type: task
complexity: B
priority: medium
status: done
created: 2026-03-25
github_issue: https://github.com/vamseeachanta/workspace-hub/issues/1404
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1404
plan_reviewed: true
plan_approved: true
spec_ref: specs/wrk/workspace-hub-1404/plan.md
stage_evidence_ref: .claude/work-queue/assets/workspace-hub-1404/evidence/stage-evidence.yaml
plan_workstations:
  - ace-linux-1
execution_workstations:
  - ace-linux-1
---

# WRK-1404: Organize /mnt/ace/docs/ subfolders and deduplicate engineering references

## Description

The recent local-analysis relocation (WRK-1384/1396) added several new subfolders to `/mnt/ace/docs/`. Review and organize the docs structure for consistency and check for duplicates across the knowledge center.

## Scope

- Review new subfolders: conferences/, engineering-refs/, engineering-drawings/, github-references/, books/, admin-refs/, sd-python-docs/, docker-examples/, tecplot/
- Check for duplicates between engineering-refs/rearrange-data/ and existing docs (DNV standards, project proposals)
- Consolidate overlapping categories (e.g., engineering-refs/ vs engineering-drawings/)
- Review docs/ naming convention — standardize folder names
- Check if docker-examples/ and sd-python-docs/ belong under docs/ or respective repos

## Related

- Parent: WRK-1384, WRK-1396
