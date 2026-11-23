# /mnt/local-analysis conservative cleanup — 2026-05-24

## Summary

User approved the full conservative cleanup set. Evidence-bearing agent folders were archived before deletion; reconstructible Python virtual environments and safe transient files were deleted.

## Disk usage after cleanup

```text
Filesystem     1024-blocks     Used Available Capacity Mounted on
/dev/sda2        976246780 47887564 928359216       5% /mnt/local-analysis
```

## Archive

- Archive: `docs/sessions/archives/2026-05-24-mnt-local-analysis-conservative-cleanup.tar.gz`
- Manifest: `docs/sessions/archives/2026-05-24-mnt-local-analysis-conservative-cleanup.manifest.tsv`
- SHA256: `docs/sessions/archives/2026-05-24-mnt-local-analysis-conservative-cleanup.sha256`
- Verification: `docs/sessions/archives/2026-05-24-mnt-local-analysis-conservative-cleanup-cleanup-verification.json`
- Archive size: `142M`
- Archive file entries: `37794`
- SHA check: `2026-05-24-mnt-local-analysis-conservative-cleanup.tar.gz: OK`

## Removed targets

- `/mnt/local-analysis/night-runs`
- `/mnt/local-analysis/git-sync-20260523-224114.log`
- `/mnt/local-analysis/ace2-codex-work` (archived)
- `/mnt/local-analysis/ace2-worker-logs` (archived)
- `/mnt/local-analysis/ace2-worker-reports` (archived)
- `/mnt/local-analysis/capytaine-env`
- `/mnt/local-analysis/cli-anything-env`
- `/mnt/local-analysis/fluids-env`
- `/mnt/local-analysis/marker-env`
- `/mnt/local-analysis/raft-env`
- `/mnt/local-analysis/sectionprops-env`
- `/mnt/local-analysis/ace2-gis-timelapse/.venv`

## Pre-delete checks

- Active process references: none found
- Hermes cron references: none found
- workspace-hub git worktree references: none found

## Notes

- `ace2-gis-timelapse` was preserved because GH issue #2538 is still open; only its reconstructible `.venv` was removed.
- The archive tarball is intentionally not staged/committed by default because compressed archives are generally gitignored and should be secret-scanned before any forced add.
