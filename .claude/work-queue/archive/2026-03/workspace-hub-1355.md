---
id: WRK-1355
title: "consolidate /mnt/ace local drive — curate relocated files, rationalize structure"
repo: workspace-hub
type: task
complexity: C
priority: medium
status: pending
created: 2026-03-24
github_issue: https://github.com/vamseeachanta/workspace-hub/issues/1355
---

# WRK-1355: consolidate /mnt/ace local drive

## Description

Consolidate and curate the `/mnt/ace/` directory on ace-linux-1 after the repo slimming initiative (WRK-1341). Multiple document/data locations exist with no canonical structure. Goal: streamlined layout for both AI and human access.

## Context

- WRK-1341 relocated ~46 GB of files from 10 git repos to `/mnt/ace/<repo>/`
- Pre-existing locations on `/mnt/ace/` are disorganized (6+ doc stores, 2 legacy HDD dumps)
- 7.3 TB drive at 65% usage — plenty of room but needs rationalization

## Acceptance Criteria

1. Audit all `/mnt/ace/` directories — map what exists and its purpose
2. Define canonical directory structure for relocated repo files
3. Merge old `digitalmodel/docs/domains/` (676 MB) with new flat structure
4. Evaluate `docs/_standards/` vs `O&G-Standards/` — deduplicate if redundant
5. Decide fate of legacy dumps (`data/va-hdd-2`, `data/2021-11-22-sd-HDD`, `_ss_repo/`)
6. Build `assets.json` manifest per ORGANIZATION_PLAN.md
7. Document final structure in a top-level README on `/mnt/ace/`

## Related

- Parent: WRK-1341 (slim down large repos)
- ORGANIZATION_PLAN.md in workspace-hub/docs/assessments/
