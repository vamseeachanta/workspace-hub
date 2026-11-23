# /mnt/ace Undiscovered Resource Audit

Generated: 2026-04-01 23:24

## Summary

| Metric | Value |
|---|---|
| GitHub repos scanned | 8 |
| Repos in catalog | 7/8 |
| Conference collections | 30 |
| Conference collections indexed | 0/30 |
| Total conference files | 38,526 |
| Standards files on disk | 26,884 |
| Standards in ledger | 364 |
| Engineering ref files | 53 |

## 1. GitHub Repos

| Repo | Last Updated | In Catalog | Domain |
|---|---|---|---|
| WEC-Sim | 2026-01-21 | Yes | hydrodynamics |
| openfast | 2026-03-12 | Yes | marine_offshore |
| gmsh | 2026-03-24 | Yes | cad_geometry |
| capytaine | 2026-03-13 | Yes | hydrodynamics |
| HAMS | 2023-09-08 | Yes | hydrodynamics |
| MoorDyn | 2026-02-20 | Yes | marine_offshore |
| MoorPy | 2025-09-19 | Yes | marine_offshore |
| opm-common | 2026-03-24 | **NO** | reservoir_simulation |

## 2. Conference Collections

| Conference | Files | Indexed |
|---|---|---|
| OMAE | 13,126 | **NO** |
| OTC | 8,500 | **NO** |
| DOT | 7,516 | **NO** |
| ISOPE | 4,516 | **NO** |
| UK Conference Folder | 2,725 | **NO** |
| NACE | 561 | **NO** |
| Flow Induced Vibration | 229 | **NO** |
| Arctic Technology Conference | 216 | **NO** |
| Subsea Tieback | 214 | **NO** |
| SPE | 129 | **NO** |
| Offshore West Africa | 125 | **NO** |
| TOD | 101 | **NO** |
| SNAME | 99 | **NO** |
| Coiled Tubing & Well Intervention Conference 2011 | 68 | **NO** |
| TO SORT | 67 | **NO** |
| Rio Oil & Gas | 66 | **NO** |
| DeepGulf | 43 | **NO** |
| ISO 9001 | 37 | **NO** |
| Subsea Survey IMMR | 34 | **NO** |
| Robert Restore | 24 | **NO** |
| Euroforum Offshore Risers | 23 | **NO** |
| EUCI | 20 | **NO** |
| IMarEST Offshore Oil and Gas Conference | 20 | **NO** |
| Subsea Houston | 20 | **NO** |
| Unlocking Deepwarter Potential- Mumbai | 20 | **NO** |
| IADC International Deepwater Drilling | 15 | **NO** |
| Dry Tree Forum | 5 | **NO** |
| Pipeline Pigging & Integrity Management Feb 2009 | 5 | **NO** |
| JPT | 1 | **NO** |
| SUT | 1 | **NO** |

## 3. O&G Standards Coverage

| Org | Files on Disk | In Ledger | Coverage % |
|---|---|---|---|
| ASTM | 25,537 | 97 | 0.4% |
| API | 574 | 178 | 31.0% |
| ISO | 308 | 64 | 20.8% |
| SNAME | 145 | 0 | 0.0% |
| DNV | 100 | 22 | 22.0% |
| OnePetro | 94 | 0 | 0.0% |
| BSI | 76 | 0 | 0.0% |
| ABS | 30 | 3 | 10.0% |
| Norsok | 9 | 0 | 0.0% |
| MIL | 7 | 0 | 0.0% |
| NEMA | 4 | 0 | 0.0% |

## 4. Engineering References

Top-level files: 31

| Subdirectory | Files |
|---|---|
| api | 3 |
| dnv | 3 |
| drilling | 4 |
| fea | 4 |
| general | 8 |

## Top 20 Undiscovered Resources by Estimated Value

| Rank | Resource | Score | Recommendation |
|---|---|---|---|
| 1 | Conference: DOT (7,516 files) | 100 | Index into document-index |
| 2 | Conference: ISOPE (4,516 files) | 100 | Index into document-index |
| 3 | Conference: OMAE (13,126 files) | 100 | Index into document-index |
| 4 | Conference: OTC (8,500 files) | 100 | Index into document-index |
| 5 | Conference: UK Conference Folder (2,725 files) | 100 | Index into document-index |
| 6 | Standards: ASTM (25,440 unledgered) | 100 | Add to standards-transfer-ledger |
| 7 | Repo: opm-common (not in catalog) | 80 | Add to open-source-engineering-catalog.yaml |
| 8 | Conference: NACE (561 files) | 56 | Index into document-index |
| 9 | Eng-refs: 31 loose top-level files | 31 | Organize into subdirs and catalog |
| 10 | Conference: Flow Induced Vibration (229 files) | 22 | Index into document-index |
| 11 | Conference: Arctic Technology Conference (216 files) | 21 | Index into document-index |
| 12 | Conference: Subsea Tieback (214 files) | 21 | Index into document-index |
| 13 | Eng-refs: general (8 files) | 16 | Catalog and cross-reference |
| 14 | Conference: Offshore West Africa (125 files) | 12 | Index into document-index |
| 15 | Conference: SPE (129 files) | 12 | Index into document-index |
| 16 | Conference: TOD (101 files) | 10 | Index into document-index |
| 17 | Conference: SNAME (99 files) | 9 | Index into document-index |
| 18 | Eng-refs: drilling (4 files) | 8 | Catalog and cross-reference |
| 19 | Eng-refs: fea (4 files) | 8 | Catalog and cross-reference |
| 20 | Standards: API (396 unledgered) | 7 | Add to standards-transfer-ledger |

## Recommendations for Next Indexing Batch

1. **Index conference papers** — 30 conference collections with ~36K files are completely unindexed.
   Priority: OMAE (13K), OTC (8.5K), DOT (7.5K), ISOPE (4.5K).
2. **Catalog opm-common** — The only cloned repo not in the OSS catalog.
3. **Expand standards ledger** — ASTM has 25K+ files but only ~97 ledger entries (<0.4% coverage).
4. **Engineering refs** — 31 loose files + 5 subdirs need cataloging.
5. **Run full document-index sweep** on /mnt/ace/docs/conferences/ to bring them into index.jsonl.
