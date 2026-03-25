---
id: WRK-1354
title: "frontierdeepwater: sync missing files from remote to /mnt/ace/frontierdeepwater"
repo: frontierdeepwater
type: task
complexity: B
priority: medium
status: pending
created: 2026-03-24
github_issue: https://github.com/vamseeachanta/workspace-hub/issues/1354
---

# WRK-1354: frontierdeepwater file sync

## Description

Compare files in the remote source directory against the local destination and copy any missing files.

- **Source (remote):** `/mnt/remote/ace-linux-2/local-analysis/workspace-hub/frontierdeepwater`
- **Destination (local):** `/mnt/ace/frontierdeepwater`

## Acceptance Criteria

1. Identify all files present in source but missing from destination
2. Copy missing files to destination, preserving directory structure
3. Log which files were copied
4. Do not overwrite existing files at destination
