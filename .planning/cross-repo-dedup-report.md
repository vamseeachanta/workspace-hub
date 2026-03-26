# Cross-Repo Deduplication Report
> digitalmodel vs O&G-Standards | Generated 2026-03-25

## Summary

| Metric | Value |
|---|---|
| digitalmodel files (excl .git) | 124142 |
| O&G-Standards files (excl .git) | 57029 |
| Filename matches | 31801 |
| Exact duplicates (same name + hash) | 62 |
| Same name, different size | 31397 |
| Same name + size, different hash | 342 |
| **Estimated space savings** | **82.49 MB** |

## Methodology
- Pass 1: matched files by basename across both repos (excluding .git/)
- Pass 2: for basename matches, compared file sizes; for same-size files, computed MD5 hashes
- Exact duplicate = same basename + same MD5 hash

## Exact Duplicates (Top 50 by Size)

These files are byte-identical across both repos.

| File | Size | digitalmodel path | O&G-Standards path |
|---|---|---|---|
| `DNV-RP-F105.pdf` | 11.21 MB | `docs/domain/references/literature/engineering/Riser Engineering/Shear7/DNV-RP-F105.pdf` | `raw/Oil and Gas Codes/DNV Standards/DNV-RP-F105.pdf` |
| `DNV-RP-F105.pdf` | 11.21 MB | `docs/domain/references/literature/engineering/Riser Engineering/Shear7/DNV-RP-F105.pdf` | `raw/0000 Codes & Standards/Spare/DNV Standards/DNV-RP-F105.pdf` |
| `DNV-RP-F105.pdf` | 11.21 MB | `docs/domain/references/literature/engineering/Riser Engineering/Shear7/DNV-RP-F105.pdf` | `DNV/Recommended-Practices/DNV-RP-F105.pdf` |
| `API RP 1111 4th Ed (2009) Design, Construction, Operation, and Maintenance of Offshore Hydrocarbon Pipelines (Limit State Design).pdf` | 5.20 MB | `docs/legacy/literature/apirp2rd/Ref/API RP 1111 4th Ed (2009) Design, Construction, Operation, and Maintenance of Offshore Hydrocarbon Pipelines (Limit State Design).pdf` | `raw/0000 Codes & Standards/unsorted/API RP 1111 4th Ed (2009) Design, Construction, Operation, and Maintenance of Offshore Hydrocarbon Pipelines (Limit State Design).pdf` |
| `API RP 1111 4th Ed (2009) Design, Construction, Operation, and Maintenance of Offshore Hydrocarbon Pipelines (Limit State Design).pdf` | 5.20 MB | `docs/legacy/literature/apirp2rd/Ref/API RP 1111 4th Ed (2009) Design, Construction, Operation, and Maintenance of Offshore Hydrocarbon Pipelines (Limit State Design).pdf` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 1111/API RP 1111 4th Ed (2009) Design, Construction, Operation, and Maintenance of Offshore Hydrocarbon Pipelines (Limit State Design).pdf` |
| `API RP 1111 4th Ed (2009) Design, Construction, Operation, and Maintenance of Offshore Hydrocarbon Pipelines (Limit State Design).pdf` | 5.20 MB | `docs/guides/literature/legacy/apirp2rd/Ref/API RP 1111 4th Ed (2009) Design, Construction, Operation, and Maintenance of Offshore Hydrocarbon Pipelines (Limit State Design).pdf` | `raw/0000 Codes & Standards/unsorted/API RP 1111 4th Ed (2009) Design, Construction, Operation, and Maintenance of Offshore Hydrocarbon Pipelines (Limit State Design).pdf` |
| `API RP 1111 4th Ed (2009) Design, Construction, Operation, and Maintenance of Offshore Hydrocarbon Pipelines (Limit State Design).pdf` | 5.20 MB | `docs/guides/literature/legacy/apirp2rd/Ref/API RP 1111 4th Ed (2009) Design, Construction, Operation, and Maintenance of Offshore Hydrocarbon Pipelines (Limit State Design).pdf` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 1111/API RP 1111 4th Ed (2009) Design, Construction, Operation, and Maintenance of Offshore Hydrocarbon Pipelines (Limit State Design).pdf` |
| `API STD 2RD 2nd Ed (2013) Dynamic Risers for Floating Production Systems.pdf` | 4.10 MB | `docs/legacy/literature/apirp2rd/Ref/API STD 2RD 2nd Ed (2013) Dynamic Risers for Floating Production Systems.pdf` | `raw/0000 Codes & Standards/unsorted/API STD 2RD 2nd Ed (2013) Dynamic Risers for Floating Production Systems.pdf` |
| `API STD 2RD 2nd Ed (2013) Dynamic Risers for Floating Production Systems.pdf` | 4.10 MB | `docs/legacy/literature/apirp2rd/Ref/API STD 2RD 2nd Ed (2013) Dynamic Risers for Floating Production Systems.pdf` | `raw/0000 Codes & Standards/AS/API/API Standards/API STD 2RD/API STD 2RD 2nd Ed (2013) Dynamic Risers for Floating Production Systems.pdf` |
| `API STD 2RD 2nd Ed (2013) Dynamic Risers for Floating Production Systems.pdf` | 4.10 MB | `docs/guides/literature/legacy/apirp2rd/Ref/API STD 2RD 2nd Ed (2013) Dynamic Risers for Floating Production Systems.pdf` | `raw/0000 Codes & Standards/unsorted/API STD 2RD 2nd Ed (2013) Dynamic Risers for Floating Production Systems.pdf` |
| `API STD 2RD 2nd Ed (2013) Dynamic Risers for Floating Production Systems.pdf` | 4.10 MB | `docs/guides/literature/legacy/apirp2rd/Ref/API STD 2RD 2nd Ed (2013) Dynamic Risers for Floating Production Systems.pdf` | `raw/0000 Codes & Standards/AS/API/API Standards/API STD 2RD/API STD 2RD 2nd Ed (2013) Dynamic Risers for Floating Production Systems.pdf` |
| `API RP 2RD 1st Ed with errata (2009) Design of Risers for FPSs and TLPs.pdf` | 2.86 MB | `docs/legacy/literature/apirp2rd/Ref/API RP 2RD 1st Ed with errata (2009) Design of Risers for FPSs and TLPs.pdf` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 2RD/API RP 2RD 1st Ed with errata (2009) Design of Risers for FPSs and TLPs.pdf` |
| `API RP 2RD 1st Ed with errata (2009) Design of Risers for FPSs and TLPs.pdf` | 2.86 MB | `docs/guides/literature/legacy/apirp2rd/Ref/API RP 2RD 1st Ed with errata (2009) Design of Risers for FPSs and TLPs.pdf` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 2RD/API RP 2RD 1st Ed with errata (2009) Design of Risers for FPSs and TLPs.pdf` |
| `OTC-7325-MS.pdf` | 914.29 KB | `docs/coiled-tubing/literature/OTC-7325-MS.pdf` | `raw/0000 Codes & Standards/OnePetro/OTC-7325-MS.pdf` |
| `OTC-7325-MS.pdf` | 914.29 KB | `docs/coiled-tubing/literature/OTC-7325-MS.pdf` | `OnePetro/OTC-7325-MS.pdf` |
| `SPE-163884-MS.pdf` | 815.68 KB | `docs/coiled-tubing/literature/SPE-163884-MS.pdf` | `raw/0000 Codes & Standards/OnePetro/SPE-163884-MS.pdf` |
| `SPE-163884-MS.pdf` | 815.68 KB | `docs/coiled-tubing/literature/SPE-163884-MS.pdf` | `OnePetro/SPE-163884-MS.pdf` |
| `DNV OS F201 (2010) Dynamic Risers.pdf` | 768.66 KB | `docs/legacy/literature/apirp2rd/Ref/DNV OS F201 (2010) Dynamic Risers.pdf` | `raw/0000 Codes & Standards/DNV/DNV Offshore Standard/DNV OS F201/DNV OS F201 (2010) Dynamic Risers.pdf` |
| `DNV OS F201 (2010) Dynamic Risers.pdf` | 768.66 KB | `docs/guides/literature/legacy/apirp2rd/Ref/DNV OS F201 (2010) Dynamic Risers.pdf` | `raw/0000 Codes & Standards/DNV/DNV Offshore Standard/DNV OS F201/DNV OS F201 (2010) Dynamic Risers.pdf` |
| `DNV RP B401 (2011) Cathodic Protection Design.pdf` | 471.13 KB | `docs/cathodic_protection/literature/codes/DNV RP B401 (2011) Cathodic Protection Design.pdf` | `raw/0000 Codes & Standards/DNV/DNV Recommended Practices/DNV RP B401/DNV RP B401 (2011) Cathodic Protection Design.pdf` |
| `Jeanjean, P. 2002 - Innovative Design Method for Deepwater .pdf` | 276.45 KB | `docs/references/literature/geotech/Jeanjean, P. 2002 - Innovative Design Method for Deepwater .pdf` | `raw/Oil and Gas Codes/Papers/Reference documents/Jeanjean, P. 2002 - Innovative Design Method for Deepwater .pdf` |
| `Jeanjean, P. 2002 - Innovative Design Method for Deepwater .pdf` | 276.45 KB | `docs/references/literature/geotech/Jeanjean, P. 2002 - Innovative Design Method for Deepwater .pdf` | `raw/0000 Codes & Standards/Spare/Papers/Reference documents/Jeanjean, P. 2002 - Innovative Design Method for Deepwater .pdf` |
| `style.did` | 768 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/style/style.did` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/style/style.did` |
| `style.wld` | 608 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/style/style.wld` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/style/style.wld` |
| `style.pdd` | 373 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/style/style.pdd` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/style/style.pdd` |
| `style.stp` | 10 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/style/style.stp` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/style/style.stp` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/work/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/work/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/work/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/trans/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/work/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/topicidx/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/work/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/temp/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/work/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/morgue/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/work/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/assists/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/trans/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/work/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/trans/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/trans/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/trans/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/topicidx/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/trans/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/temp/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/trans/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/morgue/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/trans/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/assists/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/topicidx/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/work/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/topicidx/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/trans/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/topicidx/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/topicidx/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/topicidx/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/temp/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/topicidx/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/morgue/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/topicidx/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/assists/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/temp/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/work/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/temp/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/trans/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/temp/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/topicidx/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/temp/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/temp/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/temp/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/morgue/acrocat.cat` |
| `acrocat.cat` | 3 B | `docs/domain/references/literature/engineering/Machinerys Handbook/MH26/index/temp/acrocat.cat` | `raw/0000 Codes & Standards/AS/API/API Recommended Practice/API RP 579/cd/index/assists/acrocat.cat` |

## Same Name, Different Content (Top 30 by Size)

These share a filename but differ in content -- review before deduplicating.

| File | Size (digitalmodel) | Size (O&G-Standards) | Match Type |
|---|---|---|---|
| `AWS D1.1 (2006) - Structual Welding Code - Steel (Scanned).pdf` | 72.56 MB | 69.48 MB | Different size |
| `Thumbs.db` | 9.06 MB | 9.50 KB | Different size |
| `Thumbs.db` | 9.06 MB | 9.50 KB | Different size |
| `Thumbs.db` | 9.06 MB | 9.50 KB | Different size |
| `Thumbs.db` | 9.06 MB | 9.00 KB | Different size |
| `Thumbs.db` | 9.06 MB | 9.00 KB | Different size |
| `Thumbs.db` | 9.06 MB | 84.50 KB | Different size |
| `Thumbs.db` | 9.06 MB | 83.00 KB | Different size |
| `Thumbs.db` | 9.06 MB | 8.00 KB | Different size |
| `Thumbs.db` | 9.06 MB | 6.00 KB | Different size |
| `Thumbs.db` | 9.06 MB | 59.00 KB | Different size |
| `Thumbs.db` | 9.06 MB | 5.50 KB | Different size |
| `Thumbs.db` | 9.06 MB | 49.00 KB | Different size |
| `Thumbs.db` | 9.06 MB | 40.50 KB | Different size |
| `Thumbs.db` | 9.06 MB | 37.00 KB | Different size |
| `Thumbs.db` | 9.06 MB | 31.50 KB | Different size |
| `Thumbs.db` | 9.06 MB | 29.50 KB | Different size |
| `Thumbs.db` | 9.06 MB | 29.50 KB | Different size |
| `Thumbs.db` | 9.06 MB | 29.50 KB | Different size |
| `Thumbs.db` | 9.06 MB | 27.00 KB | Different size |
| `Thumbs.db` | 9.06 MB | 24.50 KB | Different size |
| `Thumbs.db` | 9.06 MB | 24.00 KB | Different size |
| `Thumbs.db` | 9.06 MB | 23.00 KB | Different size |
| `Thumbs.db` | 9.06 MB | 23.00 KB | Different size |
| `Thumbs.db` | 9.06 MB | 22.50 KB | Different size |
| `Thumbs.db` | 9.06 MB | 22.00 KB | Different size |
| `Thumbs.db` | 9.06 MB | 20.00 KB | Different size |
| `Thumbs.db` | 9.06 MB | 19.50 KB | Different size |
| `Thumbs.db` | 9.06 MB | 19.50 KB | Different size |
| `Thumbs.db` | 9.06 MB | 19.50 KB | Different size |

## File Extension Breakdown of Exact Duplicates

| Extension | Count | Total Size |
|---|---|---|
| .pdf | 22 | 82.49 MB |
| .did | 1 | 768 B |
| .wld | 1 | 608 B |
| .pdd | 1 | 373 B |
| .cat | 36 | 108 B |
| .stp | 1 | 10 B |

## Recommendations

1. **Exact duplicates (62 files, ~82 MB)**: The significant duplicates are all PDFs -- engineering standards (DNV, API, SPE/OTC papers). O&G-Standards is the authoritative standards library. Remove these PDFs from digitalmodel and, if needed, add a symlink or gitmodule reference.
2. **Thumbs.db files**: Both repos contain Windows thumbnail caches. These are safe to delete everywhere and should be added to .gitignore.
3. **Same-name divergent files (31,739 total)**: Overwhelmingly Thumbs.db and generic filenames. The one substantive case is AWS D1.1 welding code PDF (different scans, ~70 MB each). Keep whichever has better scan quality.
4. **Quick wins**: Deleting exact-duplicate PDFs from digitalmodel saves ~82 MB. Purging all Thumbs.db across both repos could save significantly more.

---
*Raw data: /tmp/dedup-work/{index_a.tsv, index_b.tsv, name_matches.tsv, hash_results.tsv}*
