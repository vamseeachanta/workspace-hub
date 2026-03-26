# Cross-Repo Dedup Cleanup: digitalmodel
> Executed 2026-03-25

## What was done

Removed exact-duplicate files from `/mnt/ace/digitalmodel/` that already exist in the authoritative O&G-Standards repo. Files were moved (not deleted) to a staging trash directory for safe rollback.

## Results

| Metric | Value |
|---|---|
| Files moved | 21 |
| PDFs removed | 13 |
| Trivial files removed (style.*, acrocat.cat) | 8 |
| Space freed | 39.48 MB |

## PDFs Removed (13 unique files)

| File | digitalmodel path |
|---|---|
| DNV-RP-F105.pdf | `docs/domain/references/literature/engineering/Riser Engineering/Shear7/` |
| API RP 1111 4th Ed (2009)...pdf | `docs/legacy/literature/apirp2rd/Ref/` |
| API RP 1111 4th Ed (2009)...pdf | `docs/guides/literature/legacy/apirp2rd/Ref/` |
| API STD 2RD 2nd Ed (2013)...pdf | `docs/legacy/literature/apirp2rd/Ref/` |
| API STD 2RD 2nd Ed (2013)...pdf | `docs/guides/literature/legacy/apirp2rd/Ref/` |
| API RP 2RD 1st Ed (2009)...pdf | `docs/legacy/literature/apirp2rd/Ref/` |
| API RP 2RD 1st Ed (2009)...pdf | `docs/guides/literature/legacy/apirp2rd/Ref/` |
| OTC-7325-MS.pdf | `docs/coiled-tubing/literature/` |
| SPE-163884-MS.pdf | `docs/coiled-tubing/literature/` |
| DNV OS F201 (2010)...pdf | `docs/legacy/literature/apirp2rd/Ref/` |
| DNV OS F201 (2010)...pdf | `docs/guides/literature/legacy/apirp2rd/Ref/` |
| DNV RP B401 (2011)...pdf | `docs/cathodic_protection/literature/codes/` |
| Jeanjean, P. 2002...pdf | `docs/references/literature/geotech/` |

## Trivial Files Removed (8 files from Machinery's Handbook MH26 index)

- `index/style/style.did`, `style.wld`, `style.pdd`, `style.stp`
- `index/work/acrocat.cat`, `index/trans/acrocat.cat`, `index/topicidx/acrocat.cat`, `index/temp/acrocat.cat`

## Rollback

Files preserved at `/tmp/dedup-trash/digitalmodel-cross-repo/` with original directory structure.
Full manifest: `/tmp/dedup-trash/digitalmodel-cross-repo/manifest.log`

To restore any file:
```bash
# Example: restore a single file
cp "/tmp/dedup-trash/digitalmodel-cross-repo/docs/coiled-tubing/literature/OTC-7325-MS.pdf" \
   "/mnt/ace/digitalmodel/docs/coiled-tubing/literature/OTC-7325-MS.pdf"
```

## Notes

- The dedup report listed 22 PDF "rows" but many were the same digitalmodel file matching multiple O&G-Standards locations. The 13 unique digitalmodel PDF paths account for all 22 cross-repo duplicate pairs.
- The report estimated 82.49 MB savings counting each (source, target) pair; actual unique-file savings is 39.48 MB since each digitalmodel file was counted once.
