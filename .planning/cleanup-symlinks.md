# Post-Dedup Symlink Cleanup
> Date: 2026-03-25 | Scope: digitalmodel -> O&G-Standards

## What was done

After removing 22 exact-duplicate PDFs (~82 MB) from `digitalmodel`, relative symlinks
were created at every original path so that existing references continue to resolve.
A YAML manifest was also created for programmatic lookups.

## Artifacts

| Artifact | Path |
|---|---|
| Reference manifest | `/mnt/ace/digitalmodel/docs/standards-references.yaml` |
| Dedup report (source) | `.planning/cross-repo-dedup-report.md` |

## Symlinks created (13 links, 9 unique standards)

All symlinks are relative, rooted through `../../...O&G-Standards/`.

| # | digitalmodel path | canonical O&G-Standards path | Standard |
|---|---|---|---|
| 1 | `docs/domain/references/literature/engineering/Riser Engineering/Shear7/DNV-RP-F105.pdf` | `DNV/Recommended-Practices/DNV-RP-F105.pdf` | DNV-RP-F105 |
| 2 | `docs/legacy/literature/apirp2rd/Ref/API RP 1111 ...pdf` | `raw/.../API RP 1111/API RP 1111 ...pdf` | API RP 1111 |
| 3 | `docs/guides/literature/legacy/apirp2rd/Ref/API RP 1111 ...pdf` | (same as #2) | API RP 1111 |
| 4 | `docs/legacy/literature/apirp2rd/Ref/API STD 2RD ...pdf` | `raw/.../API STD 2RD/API STD 2RD ...pdf` | API STD 2RD |
| 5 | `docs/guides/literature/legacy/apirp2rd/Ref/API STD 2RD ...pdf` | (same as #4) | API STD 2RD |
| 6 | `docs/legacy/literature/apirp2rd/Ref/API RP 2RD ...pdf` | `raw/.../API RP 2RD/API RP 2RD ...pdf` | API RP 2RD |
| 7 | `docs/guides/literature/legacy/apirp2rd/Ref/API RP 2RD ...pdf` | (same as #6) | API RP 2RD |
| 8 | `docs/coiled-tubing/literature/OTC-7325-MS.pdf` | `OnePetro/OTC-7325-MS.pdf` | OTC-7325-MS |
| 9 | `docs/coiled-tubing/literature/SPE-163884-MS.pdf` | `OnePetro/SPE-163884-MS.pdf` | SPE-163884-MS |
| 10 | `docs/legacy/literature/apirp2rd/Ref/DNV OS F201 ...pdf` | `raw/.../DNV OS F201/DNV OS F201 ...pdf` | DNV OS F201 |
| 11 | `docs/guides/literature/legacy/apirp2rd/Ref/DNV OS F201 ...pdf` | (same as #10) | DNV OS F201 |
| 12 | `docs/cathodic_protection/literature/codes/DNV RP B401 ...pdf` | `raw/.../DNV RP B401/DNV RP B401 ...pdf` | DNV RP B401 |
| 13 | `docs/references/literature/geotech/Jeanjean, P. 2002 ...pdf` | `raw/.../Reference documents/Jeanjean, P. 2002 ...pdf` | Jeanjean-2002 |

## Verification

All 13 symlinks were verified as resolving (`-L` and `-e` checks passed).
Zero broken references after dedup.

## Not covered

- The dedup report also listed 40 non-PDF exact duplicates (`.did`, `.wld`, `.pdd`, `.stp`,
  `.cat` files from Machinery's Handbook index data). These are tiny files (< 2 KB total)
  with coincidental name matches against API RP 579 CD index files -- not true cross-repo
  duplicates worth symlinking. They were excluded.
- Same-name-different-content files (31,739 entries, mostly `Thumbs.db`) were not touched.
  The recommendation stands to purge all `Thumbs.db` and add to `.gitignore`.
