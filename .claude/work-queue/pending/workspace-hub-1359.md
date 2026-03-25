---
id: WRK-1359
title: "extend assets.json with file-level inventory"
repo: workspace-hub
type: task
complexity: B
priority: medium
status: pending
created: 2026-03-25
exec_order: 6
depends_on: [WRK-1357, WRK-1363]
github_issue: https://github.com/vamseeachanta/workspace-hub/issues/1359
---

# WRK-1359: extend assets.json with file-level inventory

## Description

Extend the existing assets.json manifest to include file-level inventory entries for each relocated directory on /mnt/ace/. Currently assets.json tracks directory-level metadata; this task adds per-file records with size, hash, and domain tags to support downstream curation and dedup workflows.

## Related

- Parent: WRK-1355
