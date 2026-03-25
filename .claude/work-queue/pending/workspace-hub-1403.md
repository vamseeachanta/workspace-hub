---
id: WRK-1403
title: "Clean stale NTFS remnants from local-analysis after remount"
repo: workspace-hub
type: task
complexity: A
priority: low
status: pending
created: 2026-03-25
github_issue: https://github.com/vamseeachanta/workspace-hub/issues/1403
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1403
---

# WRK-1403: Clean stale NTFS remnants from local-analysis after remount

## Description

After remounting /mnt/remote/ace-linux-2, remove leftover items that couldn't be deleted due to stale file handles and permission errors on the Samba/NTFS mount.

## Scope

- Delete `Dropbox/` (empty, permission error on Samba)
- Delete `OneDrive` broken symlink (NTFS reparse point)
- Verify `0000 Conferences` and `0000 www` skeleton directories are gone (stale handle remnants)
- Confirm only `workspace-hub/` remains in `/mnt/remote/ace-linux-2/local-analysis/`

## Related

- Parent: WRK-1384, WRK-1396
