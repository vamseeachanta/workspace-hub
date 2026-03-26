---
wrk_id: WRK-1362
title: Fix broken README_MIGRATED.md pointers in /mnt/ace/docs/
route: A
status: draft
---

# WRK-1362: Fix broken README_MIGRATED.md pointers

## Summary

99 README_MIGRATED.md files under `/mnt/ace/docs/` point to non-existent
`/mnt/ace/docs/clients/unknown/projects/<slug>` paths. The actual project
directories live under `/mnt/ace/docs/disciplines/<category>/projects/<slug>`.

## Acceptance Criteria

1. All 99 README_MIGRATED.md files point to directories that exist
2. No README_MIGRATED.md file references `/clients/unknown/` paths
3. A verification scan reports 0 broken pointers after the fix

## Pseudocode

```
1. find all README_MIGRATED.md under /mnt/ace/docs/
2. for each file:
   a. extract target path from "New location:" line
   b. if target dir exists → skip (already valid)
   c. extract project slug (basename of target)
   d. search /mnt/ace/docs/disciplines/ for matching directory
   e. if match found → rewrite "New location:" line with actual path
   f. if no match → log as unresolvable error
3. run verification scan: count remaining broken pointers
```

## Test Plan

| # | Test | Expected |
|---|------|----------|
| 1 | Count broken pointers before fix | 99 |
| 2 | Run fix script | All 99 updated |
| 3 | Count broken pointers after fix | 0 |
| 4 | Spot-check 3 random files | Correct paths pointing to existing dirs |
