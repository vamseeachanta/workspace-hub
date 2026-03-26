# Cross-Repo Version Arbitration Report
> digitalmodel vs O&G-Standards | Generated 2026-03-25

## Summary

| Metric | Value |
|---|---|
| Original same-name+same-size+different-hash pairs | 342 |
| Already cleaned (Thumbs.db etc.) | 341 |
| Remaining same-name+same-size pairs (fresh scan) | 14 |
| Exact duplicates (still present, trivial) | 13 |
| True version conflicts (same name, different content) | 1 |
| Same-name PDFs with different sizes (version variants) | 2 unique documents |
| **Actionable items** | **3** |

## Status of Original 342 Pairs

The original 342 "same name + same size + different hash" pairs from the dedup report were overwhelmingly Thumbs.db files. These have since been cleaned from both repos. Of the 404 same-name+same-size pairs in the original data:

- **341 pairs**: both files deleted (Thumbs.db cleanup)
- **28 pairs**: digitalmodel file deleted, O&G-Standards copy remains
- **35 pairs**: both still exist (34 exact, 1 diff)

The prior exact-duplicate cleanup already symlinked all significant PDF duplicates (DNV-RP-F105, API RP 1111, API STD 2RD, API RP 2RD, OTC-7325-MS, SPE-163884-MS, DNV OS F201, DNV RP B401, Jeanjean 2002). Verified: all are now symlinks in digitalmodel pointing to O&G-Standards.

## Remaining Version Conflicts

### 1. `data.trn` -- Same name+size, different content (TRIVIAL)

| Attribute | digitalmodel | O&G-Standards |
|---|---|---|
| Path | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/trans/data.trn` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/trans/data.trn` |
| Size | 97 bytes | 97 bytes |
| MD5 | `bab4f91f7c4a92b2f7421d0e6bb40177` | `d74aeb676e3d7453a7ae77d70663353a` |
| Content | Index timestamp: Jul 05 2000 | Index timestamp: Apr 12 2000 |

**Recommendation: NO ACTION** -- These are CD-ROM index metadata files from completely different products (Machinery's Handbook MH26 vs API RP 579 CD). Same filename by coincidence, not related documents.

### 2. `API 6A.pdf` -- Different versions across repos

| Version | Location | Size | Pages | Notes |
|---|---|---|---|---|
| DM copy | `docs/guides/literature/legacy/apirp2rd/Ref/API 6A.pdf` | 843 KB | 4 | Foxit editor excerpt, 2017 |
| DM copy 2 | `docs/legacy/literature/apirp2rd/Ref/API 6A.pdf` | 843 KB | 4 | Same file, duplicate path |
| OG errata | `raw/0000 Codes & Standards/Spare/API Standards/API 6A.pdf` | 41 KB | 1 | Errata 01/03, FrameMaker 2003 |
| OG errata 2 | `raw/Oil and Gas Codes/API Standards/API 6A.pdf` | 41 KB | 1 | Same errata, duplicate path |
| OG full standard | `raw/0000 Codes & Standards/AS/API/STA/API 6A.pdf` | 4.2 MB | 422 | Full standard, 2001/2011 |

**Recommendation: MANUAL REVIEW** -- Three genuinely different documents all named "API 6A.pdf":
- The DM copy (4 pages) appears to be an excerpt or summary
- The OG 41KB copies are an errata sheet
- The OG 4.2MB copy is the full 422-page standard
- All three are useful for different purposes; no version is strictly "better"
- The DM copy should NOT be symlinked to any OG version since they are different documents

### 3. `AWS D1.1 (2006) - Structual Welding Code - Steel (Scanned).pdf` -- Different scans

| Attribute | digitalmodel | O&G-Standards |
|---|---|---|
| Path | `docs/domain/subsea-risers/riser-eng-job/2100-blk31-slor-design/Drawings/303 URA/SW3D/FLEXABLE SUPPORT FOAM/ARCHIVE - CLOSE ALL BEFORE ACCESSING!!!/NEW PROTOTYPE PARTS/BRIANS TEMPRY FOLDER DELETE/` | `raw/0000 Codes & Standards/AWS/AWS D1.1/` |
| Size | 76.1 MB | 72.9 MB |
| Pages | 529 | 529 |
| Created | Jun 27 2007 | Jun 27 2007 |
| Modified | Feb 10 2009 | May 23 2011 |

**Recommendation: keep-right (O&G-Standards), symlink from digitalmodel**
- Same page count, same creation date -- these are different compressions of the same scan
- O&G-Standards version is 3.2 MB smaller (better compression) and has a newer modification date (2011 vs 2009), suggesting re-optimization
- The DM path is deeply nested in an "ARCHIVE/DELETE" folder -- not authoritative
- O&G-Standards path (`raw/0000 Codes & Standards/AWS/AWS D1.1/`) is the proper standards location

## Remaining Exact Duplicates (Trivial, No Action Needed)

| File | Size | Count | Notes |
|---|---|---|---|
| `acrocat.cat` | 3 bytes | 12 pairs | CD-ROM index files from different products (MH26 vs API RP 579). Same content by coincidence. |
| `.gitignore` | 62 bytes | 1 pair | Repo config files, not cross-repo duplicates |

**Recommendation: NO ACTION** -- Symlinking would be semantically wrong (different products with coincidentally identical content).

## Action Plan

### Immediate (clear cases)

1. **AWS D1.1 PDF**: Replace the digitalmodel copy with a symlink to the O&G-Standards version
   - Source: `O&G-Standards/raw/0000 Codes & Standards/AWS/AWS D1.1/AWS D1.1 (2006) - Structual Welding Code - Steel (Scanned).pdf`
   - Target: the deeply-nested DM copy in the ARCHIVE folder
   - Space savings: ~76 MB

### Manual Review Required

2. **API 6A.pdf**: Three different documents share the same name. Decide:
   - Keep the DM 4-page excerpt as-is (it serves a different purpose than the full standard)
   - Or replace with a symlink to the full 422-page version if the excerpt is no longer needed

### No Action

3. **data.trn**: Unrelated files with the same name
4. **acrocat.cat / .gitignore**: Trivially small, semantically unrelated

## Space Impact

| Action | Savings |
|---|---|
| AWS D1.1 symlink | ~76 MB |
| API 6A (if manual review decides to symlink) | ~1.7 MB |
| **Total potential** | **~78 MB** |

---
*Data: /tmp/dedup-work/arbitration/{final_hashed.tsv, same_name_size_clean.tsv, pdf_name_matches.tsv}*
