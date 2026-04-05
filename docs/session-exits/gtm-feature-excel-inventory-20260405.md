# Session Exit — GTM Feature Work + Excel Inventory
# Date: 2026-04-05

## EXECUTIVE SUMMARY

Two major workstreams completed this session:
1. **GTM Demo Prioritization**: Prioritized 4 remaining demos, defined Demo 3 requirements, captured user design decisions
2. **Excel Inventory Phase 1**: Scanned all 4,125 Excel workbooks across workspace-hub and /mnt/ace/digitalmodel

## DEMO BUILD ORDER
Demo 3 (Mudmat 180 cases) → Demo 5 (Jumper 60 cases) → Demo 1 (Freespan 680 cases) → Demo 4 (Pipelay 60 cases)

## DESIGN DECISIONS CAPTURED
| Decision | Value |
|----------|-------|
| Splash zone method | Simplified screening — OrcaFlex governs |
| Cable weight | From existing vessel catalogs/models |
| Go/No-Go thresholds | Per DNV code utilisation factors |
| Hero chart layout | Two side-by-side heatmaps |
| Seabed bearing | Soft clay default + sensitivity chart |
| Hs sweep | 1.0, 1.5, 2.0, 2.5, 3.0m |

## CONFIRMED JUMPER REFERENCE MODELS
- manifold_to_plet (1996m, 10.75" rigid, SZ + DZ)
- plet_to_plem (same config, different endpoints)
- Full line types, coatings, connectors, vessel, clumps extracted

## EXCEL INVENTORY RESULTS
- 4,125 files scanned, 10.1 GB total
- 193 .xlsx fully scanned → 1,930 worksheets
- 3,879 .xls binary detected (xlrd needed for sheet scan)
- 310 .xls non-binary (CSV/XML)
- Top domain: riser engineering (3,730 files)
- Top projects: 2100 BLK31 (2,563), 3824 Containment (959), 3836 HP1 (280)

## GITHUB ISSUES CREATED/UPDATED
### New issues:
| # | Title |
|---|-------|
| 1910 | SCAN: Map all 3,820 Excel workbooks in docs/tests and /mnt/ace |
| 1914 | PHASE 2: Deep scan 3,879 .xls workbooks with xlrd |
| 1930 | READY: Build GTM Demo 1 — DNV Freespan/VIV Analysis |
| 1931 | READY: Build GTM Demo 3 — Deepwater Mudmat Installation |
| 1932 | INVENTORY: Complete OrcaFlex/OrcaWave model catalog |

### Updated issues:
| # | Title | Change |
|---|-------|--------|
| 1800 | GTM: 5 Interactive Demo Reports (umbrella) | Status table, build order, design decisions |
| 1871 | Demo 1 Freespan | Engineering basis, module references |
| 1872 | Demo 3 Mudmat | Refined requirements, 180 cases, Hs sweep |
| 1873 | Demo 4 Pipelay | Updated scope |
| 1874 | Demo 5 Jumper | Code reuse plan, dependencies updated |
| 1904 | OrcaFlex/OrcaWave inventory | Updated |
| 1905 | Rigid jumper model + workbook | Updated: confirmed reference models, extracted line types/coatings/etc |
| 1909 | Excel catalog (parent) | Phase 1 status, sub-issues linked |

## FILES CHANGED
- `digitalmodel/examples/demos/gtm/demo_03_requirements.md` — created
- `digitalmodel/examples/demos/gtm/session_exit_20260405.md` — created
- `workspace-hub/scripts/knowledge/excel-inventory-scan.py` — created (scanner)
- `workspace-hub/data/inventory/excel-inventory.jsonl` — created (4,125 records)
- `workspace-hub/data/inventory/excel-inventory-report.md` — created
- `workspace-hub/data/inventory/excel-sheet-detail.jsonl` — created (1,930 sheet records)

## NEXT ACTIONS (for user)
1. Build Demo 3 (Mudmat) — issue #1872/#1931 — all requirements defined, hand-held decisions captured
2. Phase 2 Excel scan (#1914) — install xlrd, deep-scan 3,879 .xls files (unlock jumper/riser data)
3. OrcaFlex model catalog (#1932) — walk 3,524 YML models, extract metadata
