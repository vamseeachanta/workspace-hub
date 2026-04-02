# Document Index — Data Audit Report

> Generated: 2026-04-01 | WRK-1179 Stream A Task 1
> Updated: 2026-04-01 — standards reclassification complete (76 entries moved from 'other')
> Re-run: see commands in WRK-1179 checkpoint

## Index Summary

| Metric | Value |
|--------|------:|
| Total records | 1,033,933 |
| With summary (Phase B) | 639,585 (61.9%) |
| Distinct sources | 6 |
| Distinct domains | 14 (index) / 10 (standards ledger) |

Phase B enrichment (AI-generated summaries) has been applied to 639,585
records (61.9% of index). Standards domain reclassification is complete —
the former 'other' catch-all domain has been fully decomposed.

## Records by Source

| Source | Count | % |
|--------|------:|--:|
| dde_project | 495,487 | 47.9% |
| ace_project | 453,285 | 43.8% |
| ace_standards | 55,442 | 5.4% |
| og_standards | 27,980 | 2.7% |
| workspace_spec | 1,587 | 0.2% |
| api_metadata | 8 | <0.1% |

## Records by Domain (Index)

| Domain | Count | % |
|--------|------:|--:|
| marine | 283,451 | 27.4% |
| cad | 275,445 | 26.6% |
| pipeline | 188,173 | 18.2% |
| materials | 72,344 | 7.0% |
| portfolio | 55,942 | 5.4% |
| structural | 50,001 | 4.8% |
| other | 44,705 | 4.3% |
| project-management | 43,922 | 4.2% |
| installation | 13,502 | 1.3% |
| energy-economics | 2,930 | 0.3% |
| cathodic-protection | 1,714 | 0.2% |
| workspace-spec | 1,587 | 0.2% |
| naval-architecture | 144 | <0.1% |
| regulatory | 73 | <0.1% |

Note: Index 'other' records (44,705) are project documents, correspondence,
and miscellaneous files — not standards. Standards 'other' has been fully
reclassified (see below).

## Standards Transfer Ledger Status

425 standards tracked across 10 domains (reclassified 2026-04-01).

The former 'other' domain (166 standards) has been fully decomposed into
proper engineering domains. Two new domains were created: `process` (55)
and `drilling` (9). Existing domains grew: materials +72, cad +22,
installation +17, regulatory +4, structural −10 (net re-mapping),
marine −4 (net re-mapping).

| Domain | Total | Done | WRK Captured | Reference | Gap |
|--------|------:|-----:|-------------:|----------:|----:|
| materials | 122 | 0 | 2 | 27 | 93 |
| structural | 72 | 4 | 3 | 41 | 24 |
| pipeline | 55 | 12 | 10 | 20 | 13 |
| process | 55 | 0 | 0 | 2 | 53 |
| marine | 33 | 4 | 1 | 26 | 2 |
| cad | 23 | 0 | 0 | 1 | 22 |
| installation | 22 | 0 | 0 | 11 | 11 |
| cathodic-protection | 19 | 9 | 6 | 2 | 2 |
| regulatory | 15 | 0 | 0 | 8 | 7 |
| drilling | 9 | 0 | 1 | 0 | 8 |
| **TOTAL** | **425** | **29** | **23** | **138** | **235** |

Completion rate: 29/425 done (6.8%), 23/425 WRK-captured (5.4%).
Gap rate: 235/425 (55.3%).

## Top Priority Gaps by Domain

### 1. materials (93 gaps) ▲ was 21
Largest gap domain after reclassification. Includes ASTM testing/metallurgy
standards (A36, A105, A106, A182, A193, A194, A216, A217, A350, A352, etc.),
ISO metallurgy standards (148, 14919, 14921), and API valve/piping standards
(526, 530, 560, 589, 598, 602, 603, 608). Critical for digitalmodel
materials module.

### 2. process (53 gaps) — NEW DOMAIN
Newly created domain from reclassification. Contains API RP standards for
process safety, fired heaters, relief devices, pressure vessels, and
facility design (API RP 14B/14E/14G, API Std 521/526/537/660/661).
Needs a dedicated WRK to begin standards absorption.

### 3. structural (24 gaps)
API RP 2A-WSD editions, ASTM fatigue/creep testing standards. Several are
directly relevant to asset integrity calculations in digitalmodel.

### 4. cad (22 gaps) ▲ was 1
Grew significantly from reclassification. Includes ISO drawing standards
(128, 129, 1101, 1302, 3098, etc.) and ASTM E1544 (Hornbeck diagrams).
Relevant to technical drawing and GD&T modules.

### 5. pipeline (13 gaps)
API RP 1110/1111/1117 (pipeline operations), DNV RP F101/F201 (corroded
pipelines, titanium risers). Directly relevant to digitalmodel pipeline
module.

### 6. installation (11 gaps) ▲ was 3
API RP 14H/1615/686 plus reclassified construction/commissioning standards.

### 7. drilling (8 gaps) — NEW DOMAIN
Newly created domain. API standards for well control, drilling equipment,
and completion operations. Needs a dedicated WRK.

### 8. regulatory (7 gaps) ▲ was 4
API RP 1604/1621/2350/536 plus reclassified tank/facility regulation
standards.

### 9. marine (2 gaps)
API RP 17A, remaining subsea standards. Nearly complete domain.

### 10. cathodic-protection (2 gaps)
API RP 651, ISO 15589-2. Nearly complete — already has 9 done, 6
WRK-captured. Best completion rate of all domains (47.4% done).

## Reclassification Impact Summary

The 'other' domain in the standards ledger has been **fully eliminated**.
All 166 former 'other' entries were reclassified:

| Destination Domain | Entries Received |
|--------------------|----------------:|
| materials | +72 |
| process (new) | +55 |
| cad | +22 |
| installation | +17 |
| drilling (new) | +9 |
| regulatory | +4 |

Note: Some entries also moved between existing domains during the
reclassification audit, resulting in net changes that differ from the
simple additions above.

The index-level 'other' domain (44,705 records / 4.3%) still exists — these
are project documents, correspondence, and miscellaneous files that are
distinct from the standards ledger.

## Recommendations

1. **Materials domain**: Now the largest gap domain (93 gaps, 0 done).
   Needs a dedicated WRK to begin standards absorption. Highest priority
   for new implementation work.
2. **Process domain**: New domain with 53 gaps. Create initial WRK items
   to begin tracking process safety and equipment standards.
3. **Pipeline + CP focus**: These domains have the best done/WRK-captured
   ratios and active digitalmodel modules — close remaining gaps here first.
4. **Phase B enrichment**: 61.9% summary coverage achieved. Continue
   AI summarization for remaining 394,348 records.
5. **CAD domain**: Grew to 22 gaps — plan ISO drawing standards integration
   for GD&T and technical documentation modules.
6. **Drilling domain**: New domain with 8 gaps. Low priority until a
   drilling-specific module is developed.
