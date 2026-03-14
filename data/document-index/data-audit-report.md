# Document Index — Data Audit Report

> Generated: 2026-03-14 | WRK-1179 Stream A Task 1
> Re-run: see commands in WRK-1179 checkpoint

## Index Summary

| Metric | Value |
|--------|------:|
| Total records | 1,033,933 |
| With summary (Phase B) | 0 (0%) |
| Distinct sources | 6 |
| Distinct domains | 14 |

Phase B enrichment (AI-generated summaries) has not yet been applied to any
records. This is the highest-leverage next step for index quality.

## Records by Source

| Source | Count | % |
|--------|------:|--:|
| dde_project | 495,487 | 47.9% |
| ace_project | 453,285 | 43.8% |
| ace_standards | 55,586 | 5.4% |
| og_standards | 27,980 | 2.7% |
| workspace_spec | 1,587 | 0.2% |
| api_metadata | 8 | <0.1% |

## Records by Domain

| Domain | Count | % |
|--------|------:|--:|
| cad | 275,445 | 26.6% |
| marine | 266,155 | 25.7% |
| pipeline | 187,860 | 18.2% |
| other | 101,471 | 9.8% |
| materials | 72,206 | 7.0% |
| portfolio | 55,942 | 5.4% |
| structural | 49,999 | 4.8% |
| installation | 13,390 | 1.3% |
| project-management | 5,029 | 0.5% |
| energy-economics | 2,918 | 0.3% |
| cathodic-protection | 1,714 | 0.2% |
| workspace-spec | 1,587 | 0.2% |
| naval-architecture | 144 | <0.1% |
| regulatory | 73 | <0.1% |

## Standards Transfer Ledger Status

425 standards tracked across 9 domains.

| Domain | Total | Done | WRK Captured | Reference | Gap |
|--------|------:|-----:|-------------:|----------:|----:|
| other | 166 | 3 | 1 | 0 | 162 |
| structural | 82 | 3 | 5 | 49 | 25 |
| pipeline | 53 | 10 | 10 | 23 | 10 |
| materials | 50 | 0 | 0 | 29 | 21 |
| marine | 37 | 4 | 1 | 26 | 6 |
| cathodic-protection | 20 | 9 | 6 | 2 | 3 |
| regulatory | 11 | 0 | 0 | 7 | 4 |
| installation | 5 | 0 | 0 | 2 | 3 |
| cad | 1 | 0 | 0 | 0 | 1 |
| **TOTAL** | **425** | **29** | **23** | **138** | **235** |

Completion rate: 29/425 done (6.8%), 23/425 WRK-captured (5.4%).
Gap rate: 235/425 (55.3%).

## Top Priority Gaps by Domain

### 1. other (162 gaps)
Largest gap domain. Contains uncategorized standards (API, ISO, ASTM) that
need triage into proper domains before implementation. Many are ISO drawing
and testing standards. Recommended action: reclassify into structural,
materials, or cad domains first.

### 2. structural (25 gaps)
API RP 2A-WSD editions, ASTM fatigue/creep testing standards, ISO drawing
standards. Several are directly relevant to asset integrity calculations in
digitalmodel.

### 3. materials (21 gaps)
API RP/Std for valves, pressure relief, and piping (526, 530, 560, 589,
598, 602, 603, 608). ISO metallurgy standards (148, 14919, 14921).
High relevance to digitalmodel materials module.

### 4. pipeline (10 gaps)
API RP 1110/1111/1117 (pipeline operations), DNV RP F101/F201 (corroded
pipelines, titanium risers). Directly relevant to digitalmodel pipeline
module.

### 5. marine (6 gaps)
API RP 14C/14J, API RP 17A, ASTM A508/A541/A859. Subsea and platform
safety standards.

### 6. regulatory (4 gaps)
API RP 1604/1621/2350/536. Tank and facility regulation standards.

### 7. cathodic-protection (3 gaps)
API 603, API RP 651, ISO 15589-2. Directly relevant to digitalmodel CP
module (already has 9 done, 6 WRK-captured).

### 8. installation (3 gaps)
API RP 14H/1615/686. Installation and commissioning standards.

### 9. cad (1 gap)
ASTM E1544 (Hornbeck diagrams). Low priority.

## Domains with Most Unclassified Records

The "other" domain contains 101,471 index records (9.8% of total) and 162
of 235 gap standards (68.9% of all gaps). This domain acts as a catch-all
and should be decomposed:

- Index records in "other" likely include project documents, correspondence,
  and miscellaneous files that need domain tagging.
- The 162 gap standards in "other" include API, ISO, and ASTM standards
  spanning welding (API 1104), storage tanks (API RP 12N/12R1), process
  safety (API RP 14B/14E/14G), and ISO drawing/testing standards.

## Recommendations

1. **Phase B enrichment**: 0% summary coverage is the top gap. Prioritize
   AI summarization for ace_standards and og_standards sources first (83,566
   records, 8.1% of index) as these are the most structured.
2. **Reclassify "other"**: Triage the 162 gap standards into proper domains
   to enable targeted WRK creation.
3. **Pipeline + CP focus**: These domains have the best done/WRK-captured
   ratios and active digitalmodel modules — close remaining gaps here first.
4. **Materials domain**: 0 done, 0 WRK-captured, 21 gaps. Needs a dedicated
   WRK to begin standards absorption.
