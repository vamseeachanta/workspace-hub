# Riser-Eng-Job PDF Dedup Cleanup

**Date:** 2026-03-26
**Source:** `/mnt/ace/digitalmodel/docs/domain/subsea-risers/riser-eng-job/`
**Report:** `riser-eng-job-dedup-report.txt` (1485 duplicate groups, 9953 total PDFs)

## Results

| Metric | Value |
|---|---|
| Duplicate groups processed | 1485 |
| Files moved to trash | 1120 |
| Space freed | 703.7 MiB (737,946,151 bytes) |
| Ambiguous groups skipped | 262 |
| Missing files (errors) | 0 |

## Decision Rules Applied

1. **SharePoint/Uploaded copies removed** -- paths containing `SharePoint/`, `To be uploaded/`, or filenames with "Downloaded from Sharepoint" were removed in favor of formal filing copies.
2. **IDC/DC/CR Comments subdirs removed** -- when a formal filing copy existed alongside a copy nested under `IDC Comments/`, `DC Comments/`, `CR Comments/`, or `Pre-issue Comments/`, the comments subfolder copy was removed.
3. **Superseded copies removed** -- copies in `Superseded/` subdirs were removed when a non-superseded formal copy existed.
4. **3824-BP MC252 tree** -- identified as a copy of the `Drawings/PDF/` tree; BP MC252 copies removed when originals existed in `Drawings/PDF/`.
5. **Formal filing dirs recognized:** DDL, DGA, RPT, DTS, PRS, MTO, SPC, RQI, SCH, PRG, MIN, RFI, DCN, TRN.

## Ambiguous Cases (262 groups, manual review needed)

Logged to `/tmp/dedup-trash/riser-eng-job/ambiguous.log`. Common patterns:

- **PRS top-level vs PRS/Installation Analysis Presentations/** -- both are valid filing locations for presentation PDFs.
- **Component Data vs Client Data vs DBA/References** -- reference material filed in multiple non-SharePoint locations.
- **Drawings/PDF/ vs Drawings/3824-BP MC252/PDF/** -- when both under `Superseded/` or same formal subdir, no clear winner.
- **Package Engineering client data** -- copies in `BP/` vs `HMC/` subdirs of uncontrolled client data folders.
- **RPT revision subdirs** -- same file in two revision folders (e.g., `Rev D1` vs `Rev 04`).

## Artifacts

- **Trash staging:** `/tmp/dedup-trash/riser-eng-job/files/` (structure preserved)
- **Move manifest:** `/tmp/dedup-trash/riser-eng-job/manifest.log`
- **Ambiguous log:** `/tmp/dedup-trash/riser-eng-job/ambiguous.log`
- **Script:** `/tmp/dedup-trash/riser-eng-job/dedup-riser.sh`

## Recovery

To restore all moved files:
```bash
cd /tmp/dedup-trash/riser-eng-job/files
find . -type f | while read f; do
  src="/mnt/ace/digitalmodel/docs/domain/subsea-risers/riser-eng-job/${f#./}"
  mkdir -p "$(dirname "$src")"
  cp "$f" "$src"
done
```

## Next Steps

- [ ] Review `ambiguous.log` (262 groups) and manually decide keepers
- [ ] Once confirmed, permanently delete `/tmp/dedup-trash/riser-eng-job/files/`
- [ ] Consider removing now-empty SharePoint/Uploaded subdirectories
