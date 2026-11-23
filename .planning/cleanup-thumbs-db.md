# Thumbs.db Cleanup — 2026-03-25

## Summary

Purged all Windows-generated `Thumbs.db` thumbnail cache files from two repositories
and added `.gitignore` rules to prevent re-introduction.

## Results

| Repo | Files removed | Space freed |
|---|---|---|
| digitalmodel | 661 | 65 MB |
| O&G-Standards | 48 | 1.2 MB |
| **Total** | **709** | **~66 MB** |

## Actions taken

1. Found 709 `Thumbs.db` files across both repos.
2. Moved all files to `/tmp/dedup-trash/thumbs-db/` organized by source repo, preserving directory structure.
3. Logged every move to `/tmp/dedup-trash/thumbs-db/manifest.log` (709 entries).
4. Created `.gitignore` in both repo roots (`/mnt/ace/digitalmodel/.gitignore`, `/mnt/ace/O&G-Standards/.gitignore`) with:
   - `Thumbs.db`
   - `.DS_Store`
   - `desktop.ini`
   - `._*`
5. Verified zero `Thumbs.db` files remain in either repo.

## Recovery

Files are staged in `/tmp/dedup-trash/thumbs-db/` with full manifest if any need to be restored.
This staging directory will be lost on reboot.
