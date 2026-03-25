---
id: WRK-1396
title: "Delete verified relocated files from local-analysis"
repo: workspace-hub
type: task
complexity: A
route: A
priority: high
status: archived
created: 2026-03-25
workstations: [ace-linux-2]
plan_workstations: [ace-linux-2]
execution_workstations: [ace-linux-2]
orchestrator: claude
plan_reviewed: true
plan_approved: true
github_issue: https://github.com/vamseeachanta/workspace-hub/issues/1396
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1396
---

# WRK-1396: Delete verified relocated files from local-analysis

## Description

User has verified the relocated files on /mnt/ace/. Delete the originals from /mnt/remote/ace-linux-2/local-analysis/ for the categories that were successfully copied in WRK-1384. Also delete system artifacts.

## Scope

- Delete relocated engineering project folders (15 folders)
- Delete relocated conferences, GDrive, www, OSI, repo, github_ref
- Delete system artifacts ($RECYCLE.BIN, System Volume Information, etc.)
- Delete OrcFxAPIConfig.py, DumpStack.log.tmp, msdia80.dll, acma_wood.ps1, Dropbox, Son_Server2

## Related

- Parent: WRK-1384
