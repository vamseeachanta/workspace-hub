---
id: WRK-1362
title: "fix broken README_MIGRATED.md pointers in /mnt/ace/docs/"
repo: workspace-hub
type: task
complexity: A
priority: high
status: archived
created: 2026-03-25
exec_order: 1
github_issue: https://github.com/vamseeachanta/workspace-hub/issues/1362
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1362
route: A
workstations: [ace-workstation]
orchestrator: claude
plan_reviewed: true
plan_approved: true
plan_workstations: [ace-workstation]
execution_workstations: [ace-workstation]
stage_evidence_ref: .claude/work-queue/assets/workspace-hub-1362/evidence/stage-evidence.yaml
percent_complete: 100
completed_at: 2026-03-25T04:54:26Z
---
# WRK-1362: fix broken README_MIGRATED.md pointers in /mnt/ace/docs/

## Description

Repair broken file-path references in README_MIGRATED.md files across /mnt/ace/docs/. After the repo slimming relocations (WRK-1341), many README_MIGRATED.md pointers still reference old in-repo paths rather than the new /mnt/ace/ locations. Scan for broken links and update them to resolve correctly.

## Related

- Parent: WRK-1355
