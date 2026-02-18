<!-- AUTO-GENERATED — do not edit by hand -->
<!-- Generated: 2026-02-18T16:47:19Z by generate-index.py -->

# Work Queue Index

> Auto-generated on 2026-02-18T16:47:19Z. Do not edit manually — run `python .claude/work-queue/scripts/generate-index.py` to regenerate.

## Summary

**Total items:** 186

### By Status

| Status | Count |
|--------|-------|
| pending | 72 |
| working | 5 |
| blocked | 3 |
| done | 1 |
| archived | 103 |

### By Priority

| Priority | Count |
|----------|-------|
| high | 72 |
| medium | 83 |
| low | 31 |

### By Complexity

| Complexity | Count |
|------------|-------|
| simple | 20 |
| medium | 68 |
| complex | 78 |

### By Repository

| Repository | Count |
|------------|-------|
| aceengineer-admin | 3 |
| aceengineer-strategy | 2 |
| aceengineer-website | 12 |
| achantas-data | 10 |
| acma-projects | 2 |
| assethold | 5 |
| assetutilities | 3 |
| digitalmodel | 77 |
| hobbies | 1 |
| investments | 1 |
| sabithaandkrishnaestates | 1 |
| workspace-hub | 32 |
| worldenergydata | 60 |

### Plan Tracking

| Metric | Count |
|--------|-------|
| Plans exist | 114 / 186 |
| Plans cross-reviewed | 31 |
| Plans approved | 30 |
| Brochure pending | 0 |
| Brochure updated/synced | 6 |

## Metrics

### Throughput

| Metric | Value |
|--------|-------|
| Total captured | 186 |
| Total archived | 103 |
| Completion rate | 103/186 (55%) |
| Monthly rate (current month) | 31 archived |
| Monthly rate (prior month) | 3 archived |

### Plan Coverage

| Metric | Count | Percentage |
|--------|-------|------------|
| Pending items with plans | 44 / 72 | 61% |
| Plans cross-reviewed | 12 | 23% |
| Plans user-approved | 13 | 25% |

### Aging

| Bucket | Count | Items |
|--------|-------|-------|
| Pending > 30 days | 0 | - |
| Pending > 14 days | 26 | WRK-005, WRK-008, WRK-015, WRK-018, WRK-019, WRK-020, WRK-021, WRK-022, WRK-023, WRK-032, WRK-036, WRK-039, WRK-041, WRK-042, WRK-043, WRK-045, WRK-046, WRK-047, WRK-048, WRK-050, WRK-075, WRK-076, WRK-080, WRK-081, WRK-084, WRK-085 |
| Working > 7 days | 0 | - |
| Blocked > 7 days | 3 | WRK-006, WRK-064, WRK-069 |

### Priority Distribution (active items only)

| Priority | Pending | Working | Blocked |
|----------|---------|---------|---------|
| High     | 16 | 5 | 1 |
| Medium   | 33  | 0  | 1  |
| Low      | 23  | 0  | 1  |

## Master Table

| ID | Title | Status | Priority | Complexity | Provider | Repos | Module | Plan? | Reviewed? | Approved? | % Done | Brochure | Blocked By |
|-----|-------|--------|----------|------------|----------|-------|--------|-------|-----------|-----------|--------|----------|------------|
| WRK-001 | Repair sink faucet in powder room at 11511 Piping Rock | archived | medium | simple | - | achantas-data | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-002 | Stove repair with factory service at 11511 Piping Rock | archived | medium | simple | - | achantas-data | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-003 | Garage clean up | archived | medium | simple | - | achantas-data | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-004 | Reorganize storage in upstairs bathroom at 11511 Piping Rock | archived | medium | simple | - | achantas-data | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-005 | Clean up email using AI (when safe) | pending | low | medium | claude | achantas-data | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-006 | Upload videos from iPhone to YouTube | blocked | low | simple | - | achantas-data | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-007 | Upload videos from Doris computer to YouTube | archived | medium | simple | - | achantas-data | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-008 | Upload photos from multiple devices to achantas-media | pending | low | medium | claude | achantas-data | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-009 | Reproduce rev30 lower tertiary BSEE field results for repeatability | archived | high | medium | - | worldenergydata | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-010 | Rerun lower tertiary analysis with latest BSEE data and validate | archived | high | medium | - | worldenergydata | - | ✅ | ❌ | ❌ | ███ 100% | - | WRK-009 |
| WRK-011 | Run BSEE analysis for all leases with field nicknames and geological era grouping | archived | high | complex | - | worldenergydata | - | ✅ | ❌ | ❌ | ███ 100% | - | WRK-010 |
| WRK-012 | Audit HSE public data coverage and identify gaps | archived | high | medium | - | worldenergydata | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-013 | HSE data analysis to identify typical mishaps by activity and subactivity | archived | high | complex | - | worldenergydata | - | ❌ | ❌ | ❌ | ███ 100% | - | WRK-012 |
| WRK-014 | HSE risk index — client-facing risk insights with risk scoring | archived | medium | complex | - | worldenergydata | - | ✅ | ❌ | ❌ | ███ 100% | - | WRK-013 |
| WRK-015 | Metocean data extrapolation to target locations using GIS and nearest-source modeling | pending | medium | complex | claude | worldenergydata | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-016 | BSEE completion and intervention activity analysis for insights | archived | medium | complex | - | worldenergydata | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-017 | Streamline BSEE field data analysis pipeline — wellbore, casing, drilling, completions, interventions | archived | high | complex | - | worldenergydata | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-018 | Extend BSEE field data pipeline to other regulatory sources (RRC, Norway, Mexico, Brazil) | pending | low | complex | claude | worldenergydata | - | ✅ | ❌ | ❌ | - | - | WRK-017 |
| WRK-019 | Establish drilling, completion, and intervention cost data by region and environment | pending | low | complex | claude+gemini | worldenergydata | - | ✅ | ❌ | ❌ | - | - | WRK-017 |
| WRK-020 | GIS skill for cross-application geospatial tools — Blender, QGIS, well plotting | pending | medium | complex | claude | digitalmodel | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-021 | Stock analysis for drastic trend changes, technical indicators, and insider trading benchmarks | pending | medium | complex | gemini | assethold | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-022 | US property valuation analysis using GIS — location, traffic, and spatial factors | pending | medium | complex | gemini | assethold | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-023 | Property GIS development timeline with future projection and Google Earth animation | pending | low | complex | claude | assethold | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-024 | Buckskin field BSEE data analysis — Keathley Canyon blocks 785, 828, 829, 830, 871, 872 | archived | high | medium | - | worldenergydata | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-025 | AQWA diffraction analysis runner | archived | high | complex | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | ✅ synced | - |
| WRK-026 | Unified input data format converter for diffraction solvers (AQWA, OrcaWave, BEMRosetta) | archived | high | complex | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-027 | AQWA batch analysis execution | archived | high | medium | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | ✅ synced | WRK-025 |
| WRK-028 | AQWA postprocessing - RAOs and verification | archived | high | complex | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | ✅ synced | WRK-025 |
| WRK-029 | OrcaWave diffraction analysis runner + file preparation | archived | high | complex | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-030 | OrcaWave batch analysis + postprocessing | archived | high | complex | - | digitalmodel | - | ✅ | ❌ | ❌ | ███ 100% | ✅ synced | WRK-029 |
| WRK-031 | Benchmark OrcaWave vs AQWA for 2-3 hulls | archived | medium | complex | claude | digitalmodel | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-032 | Modular OrcaFlex pipeline installation input with parametric campaign support | pending | medium | complex | codex | digitalmodel | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-033 | Develop OrcaFlex include-file modular skill for parametrised analysis input | archived | medium | complex | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-034 | Develop OrcaWave modular file prep skill for parametrised analysis input | archived | medium | complex | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-035 | Develop AQWA modular file prep skill for parametrised analysis input | archived | medium | complex | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-036 | OrcaFlex structure deployment analysis - supply boat side deployment with structural loads | pending | low | complex | claude | acma-projects | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-037 | Get OrcaFlex framework of agreement and terms | archived | medium | simple | - | aceengineer-admin | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-038 | Compile global LNG terminal project dataset with comprehensive parameters | archived | medium | complex | gemini | worldenergydata | - | ✅ | ❌ | ✅ | ███ 100% | - | - |
| WRK-039 | SPM project benchmarking - AQWA vs OrcaFlex | pending | medium | complex | claude | digitalmodel | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-040 | Mooring benchmarking - AQWA vs OrcaFlex | archived | medium | complex | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-041 | Develop long-term plan for Hobbies repo | pending | low | medium | gemini | hobbies | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-042 | Develop long-term plan for Investments repo | pending | low | medium | gemini | investments | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-043 | Parametric hull form analysis with RAO generation and client-facing lookup graphs | pending | low | complex | claude | digitalmodel | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-044 | Pipeline wall thickness calculations with parametric utilisation analysis | archived | medium | complex | - | digitalmodel | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-045 | OrcaFlex rigid jumper analysis - stress and VIV for various configurations | pending | medium | complex | claude | digitalmodel | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-046 | OrcaFlex drilling and completion riser parametric analysis | pending | medium | complex | claude | digitalmodel | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-047 | OpenFOAM CFD analysis capability for digitalmodel | pending | low | complex | claude | digitalmodel | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-048 | Blender working configurations for digitalmodel | pending | low | medium | codex | digitalmodel | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-049 | Determine dynacard module way forward | archived | medium | medium | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-050 | Hardware consolidation — inventory, assess, repurpose devices + dev environment readiness | pending | medium | complex | claude | workspace-hub | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-051 | digitalmodel test coverage improvement | archived | high | complex | - | digitalmodel | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-052 | assetutilities test coverage improvement | archived | high | complex | - | assetutilities | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-053 | assethold test coverage improvement | archived | medium | medium | - | assethold | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-054 | worldenergydata test coverage improvement | archived | medium | medium | - | worldenergydata | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-055 | aceengineer-website test coverage improvement | archived | low | simple | - | aceengineer-website | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-056 | aceengineer-admin test coverage improvement | archived | medium | medium | - | aceengineer-admin | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-057 | Define canonical spec.yml schema for diffraction analysis | archived | high | medium | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-058 | AQWA input backend — spec.yml to single .dat and modular deck files | archived | high | complex | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | - | WRK-057 |
| WRK-059 | OrcaWave input backend — spec.yml to single .yml and modular includes | archived | high | complex | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | - | WRK-057 |
| WRK-060 | Common mesh format and converter pipeline (BEMRosetta + GMSH) | archived | high | medium | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-061 | CLI and integration layer for spec converter | archived | medium | medium | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | - | WRK-058, WRK-059, WRK-060 |
| WRK-062 | Test suite for spec converter using existing example data | archived | high | medium | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | - | WRK-057 |
| WRK-063 | Reverse parsers — AQWA .dat and OrcaWave .yml to canonical spec.yml | archived | high | complex | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | - | WRK-057 |
| WRK-064 | OrcaFlex format converter: license-required validation and backward-compat wrapper | blocked | medium | medium | codex | digitalmodel | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-065 | S-lay pipeline installation schema + builders for PRPP Eclipse vessel | archived | high | complex | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-066 | Review and improve digitalmodel module structure for discoverability | archived | high | complex | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-067 | Acquire OSHA enforcement and fatality data | archived | high | simple | - | worldenergydata | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-068 | Acquire BSEE incident investigations and INCs data | archived | high | medium | - | worldenergydata | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-069 | Acquire USCG MISLE bulk dataset | blocked | high | simple | - | worldenergydata | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-070 | Import PHMSA pipeline data and build pipeline_safety module | archived | high | medium | - | worldenergydata | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-071 | Acquire NTSB CAROL marine investigations and EPA TRI data | archived | high | simple | - | worldenergydata | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-072 | Technical safety analysis module for worldenergydata using ENIGMA theory | archived | high | complex | - | worldenergydata | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-073 | Market digitalmodel and worldenergydata capabilities on aceengineer website | archived | high | complex | - | aceengineer-website | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-074 | Complete marine safety database importers (MAIB, IMO, EMSA, TSB) | archived | high | complex | - | worldenergydata | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-075 | OFFPIPE Integration Module — pipelay cross-validation against OrcaFlex | pending | low | complex | claude | digitalmodel | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-076 | Add data collection scheduler/orchestrator for automated refresh pipelines | pending | medium | complex | codex | worldenergydata | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-077 | Validate and wire decline curve modeling into BSEE production workflow | archived | high | medium | - | worldenergydata | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-078 | Create energy data case study — BSEE field economics with NPV/IRR workflow | archived | medium | medium | - | aceengineer-website | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-079 | Create marine safety case study — cross-database incident correlation | archived | medium | medium | - | aceengineer-website | - | ✅ | ❌ | ❌ | ███ 100% | - | WRK-074 |
| WRK-080 | Write 4 energy data blog posts for SEO | pending | low | complex | gemini | aceengineer-website | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-081 | Build interactive NPV calculator for website lead generation | pending | low | complex | codex | aceengineer-website | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-082 | Complete LNG terminal data pipeline — from config to working collection | archived | medium | medium | - | worldenergydata | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-083 | Validate multi-format export (Excel, PDF, Parquet) with real BSEE data | archived | medium | medium | - | worldenergydata | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-084 | Integrate metocean data sources into unified aggregation interface | pending | medium | complex | claude | worldenergydata | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-085 | Create public sample data access page on website | pending | low | medium | codex | aceengineer-website | - | ✅ | ❌ | ❌ | - | - | WRK-075 |
| WRK-086 | Rewrite CI workflows for Python/bash workspace | archived | medium | medium | - | workspace-hub | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-087 | Improve test coverage across workspace repos | archived | high | complex | - | workspace-hub | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-088 | Investigate and clean submodule issues (pdf-large-reader, worldenergydata, aceengineercode) | archived | low | simple | - | workspace-hub | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-089 | Review Claude Code version gap and update cc-insights | archived | low | simple | - | workspace-hub | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-090 | Identify and refactor large files exceeding 400-line limit | archived | medium | medium | - | workspace-hub | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-091 | Add dynacard module README | archived | low | low | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-092 | Register dynacard CLI entry point | archived | low | low | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-093 | Improve dynacard AI diagnostics | archived | low | complex | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | ✅ synced | - |
| WRK-094 | Plan, reassess, and improve the workspace-hub workflow | archived | high | complex | - | workspace-hub | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-096 | Review and improve worldenergydata module structure for discoverability | archived | high | medium | - | worldenergydata | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-097 | Implement three-tier data residence strategy (worldenergydata ↔ digitalmodel) | archived | high | medium | - | workspace-hub, worldenergydata, digitalmodel | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-098 | Clean up 7.1GB large data committed to worldenergydata git history | archived | high | high | - | worldenergydata | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-099 | Run 3-way benchmark on Unit Box hull | pending | medium | medium | claude | digitalmodel | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-100 | Run 3-way benchmark on Barge hull | archived | medium | medium | - | digitalmodel | - | ✅ | ❌ | ❌ | ███ 100% | - | WRK-099 |
| WRK-101 | Add mesh decimation/coarsening to mesh-utilities skill | pending | low | medium | codex | digitalmodel | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-102 | Add generic hull definition/data for all rigs in worldenergydata | archived | medium | medium | - | worldenergydata | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-103 | Add heavy construction/installation vessel data to worldenergydata | archived | medium | medium | - | worldenergydata | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-104 | Expand drilling rig fleet dataset to all offshore and onshore rigs | archived | high | complex | - | worldenergydata | - | ✅ | ✅ | ✅ | ███ 100% | - | - |
| WRK-105 | Add drilling riser component data to worldenergydata | archived | medium | medium | - | worldenergydata | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-106 | Hull panel geometry generator from waterline, section, and profile line definitions | pending | medium | complex | claude | digitalmodel | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-107 | Clarify Family Dollar 1099-MISC rent amount discrepancy ($50,085.60) | archived | high | simple | - | sabithaandkrishnaestates | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-108 | Agent usage credits display — show remaining quota at session start for weekly planning | archived | medium | medium | - | workspace-hub | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-109 | Review, refine, and curate hooks + skills — research best practices from existing workflows | archived | medium | medium | - | workspace-hub, worldenergydata, digitalmodel | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-110 | Expand hull size library with FST, LNGC, and OrcaFlex benchmark shapes | archived | medium | complex | - | digitalmodel | - | ✅ | ✅ | ✅ | ███ 100% | - | - |
| WRK-111 | BSEE field development interactive map and analytics | pending | medium | complex | claude | worldenergydata, aceengineer-website | - | ❌ | ❌ | ❌ | - | - | - |
| WRK-112 | Appliance lifecycle analytics module for assethold | pending | medium | complex | gemini | assethold | - | ❌ | ❌ | ❌ | - | - | - |
| WRK-113 | Maintain always-current data index with freshness tracking and source metadata | archived | high | medium | - | worldenergydata | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-114 | Collect hull panel shapes and sizes for various floating bodies from existing sources | archived | medium | complex | - | digitalmodel, worldenergydata | - | ❌ | ✅ | ✅ | ███ 100% | - | - |
| WRK-115 | Link RAO data to hull shapes in hull library catalog | archived | medium | medium | - | digitalmodel | - | ✅ | ✅ | ✅ | ███ 100% | - | - |
| WRK-116 | Scale hull panel meshes to target principal dimensions for hydrodynamic analysis | archived | medium | medium | - | digitalmodel | - | ❌ | ✅ | ✅ | ███ 100% | - | - |
| WRK-117 | Refine and coarsen hull panel meshes for mesh convergence sensitivity analysis | archived | medium | complex | - | digitalmodel | - | ❌ | ✅ | ✅ | ███ 100% | - | - |
| WRK-118 | AI agent utilization strategy — leverage Claude, Codex, Gemini for planning, development, testing workflows | pending | medium | complex | - | workspace-hub | - | ❌ | ❌ | ❌ | - | - | - |
| WRK-119 | Test suite optimization — tiered test profiles for commit, task, and session workflows | archived | high | complex | - | workspace-hub, worldenergydata, digitalmodel | - | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-120 | Research and purchase a smart watch | archived | low | simple | - | achantas-data | - | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-121 | Extract & Catalog OrcaFlex Models from rock-oil-field/s7 | working | high | medium | - | - | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-122 | Licensed Software Usage Workflow & Burden Reduction | archived | high | medium | - | acma-projects, assetutilities | - | ✅ | ✅ | ✅ | ███ 100% | - | - |
| WRK-124 | Session 20260211_095832 — 1 file(s) created | archived | medium | low | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-125 | OrcaFlex module roadmap — evolving coordination and progress tracking | working | high | low | - | digitalmodel | - | ✅ | ❌ | ❌ | - 10% | - | - |
| WRK-126 | Benchmark all example models across time domain and frequency domain with seed equivalence | pending | high | complex | claude | digitalmodel | - | ✅ | ✅ | ✅ | - | - | - |
| WRK-127 | Sanitize and categorize ideal spec.yml templates for OrcaFlex input across structure types | archived | high | medium | - | digitalmodel | - | ✅ | ✅ | ✅ | ███ 100% | - | WRK-121 |
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | pending | high | complex | codex | digitalmodel | - | ✅ | ✅ | ✅ | - 5% | - | - |
| WRK-130 | Standardize analysis reporting for each OrcaWave structure type | on-hold | high | complex | codex | digitalmodel | - | ✅ | ✅ | ❌ | - | - | - |
| WRK-131 | Passing ship analysis for moored vessels — AQWA-based force calculation and mooring response | working | high | complex | claude | digitalmodel | - | ✅ | ✅ | ✅ | ░░░ 25% | - | - |
| WRK-132 | Refine OrcaWave benchmarks: barge/ship/spar RAO fixes + damping/gyradii/Km comparison | archived | high | medium | codex+claude | digitalmodel | - | ✅ | ✅ | ✅ | ███ 100% | - | - |
| WRK-133 | Update OrcaFlex license agreement with addresses and 3rd-party terms | on-hold | high | medium | claude | aceengineer-admin | - | ❌ | ✅ | ❌ | - | n/a | - |
| WRK-134 | Add future-work brainstorming step before archiving completed items | archived | medium | medium | - | workspace-hub | - | ✅ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-135 | Ingest XLS historical rig fleet data (163 deepwater rigs) | archived | medium | medium | - | worldenergydata | - | ✅ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-137 | Download and parse rig spec PDFs (102 PDFs from 4 operators) | pending | low | complex | gemini | worldenergydata | - | ❌ | ❌ | ❌ | - | n/a | WRK-136 |
| WRK-138 | Fitness-for-service module enhancement: wall thickness grid, industry targeting, and asset lifecycle | archived | medium | complex | - | digitalmodel | asset_integrity | ✅ | ✅ | ✅ | ░░░ 40% | ✅ updated | - |
| WRK-139 | Develop gmsh skill and documentation | archived | medium | medium | - | workspace-hub | - | ✅ | ✅ | ✅ | ███ 100% | - | - |
| WRK-139 | Unified multi-agent orchestration architecture (Claude/Codex/Gemini) | archived | high | complex | - | workspace-hub | agents | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-140 | Integrate gmsh meshing skill into digitalmodel and solver pipelines | pending | medium | medium | codex | digitalmodel, workspace-hub | - | ❌ | ❌ | ❌ | - | - | - |
| WRK-141 | Create Achantas family tree to connect all family members | pending | medium | medium | claude | achantas-data | - | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-142 | Review work accomplishments and draft Anthropic outreach message | archived | high | medium | - | workspace-hub | - | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-143 | Full symmetric M-T envelope — closed polygon lens shapes | archived | medium | simple | - | digitalmodel | - | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-144 | API RP 2RD + API STD 2RD riser wall thickness — WSD & LRFD combined loading | archived | medium | complex | - | digitalmodel | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-145 | Design code versioning — handle changing revisions of standards | archived | medium | medium | - | digitalmodel | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-146 | Overhaul aceengineer-website: fix positioning, narrative, and social proof | pending | high | complex | claude+gemini | aceengineer-website | - | ✅ | ✅ | ✅ | - | n/a | - |
| WRK-147 | Set up aceengineer-strategy private repo with business operations framework | pending | high | complex | claude | aceengineer-strategy | - | ✅ | ✅ | ✅ | - | n/a | - |
| WRK-148 | ACE-GTM: A&CE Go-to-Market strategy stream | pending | high | complex | claude | aceengineer-website, aceengineer-strategy, workspace-hub | - | ✅ | ✅ | ✅ | - | n/a | - |
| WRK-149 | digitalmodel test coverage improvement (re-creates WRK-051) | working | high | complex | codex+claude,gemini | digitalmodel | - | ✅ | ✅ | ✅ | ░░░ 48% | n/a | - |
| WRK-150 | assetutilities test coverage improvement (re-creates WRK-052) | pending | medium | medium | claude | assetutilities | - | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-151 | worldenergydata test coverage improvement (re-creates WRK-054) | pending | medium | medium | claude | worldenergydata | - | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-152 | Marine safety importer validation — verify MAIB/TSB/IMO/EMSA importers against real data | pending | high | medium | claude | worldenergydata | marine_safety | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-153 | Energy data case study — BSEE field economics with NPV/IRR workflow | pending | medium | medium | claude | aceengineer-website | - | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-154 | CI workflow rewrite — fix 2 GitHub Actions workflows | pending | high | medium | codex | workspace-hub | - | ✅ | ✅ | ✅ | - | n/a | - |
| WRK-155 | DNV-ST-F101 submarine pipeline wall thickness — WSD and LRFD methods | pending | high | complex | claude | digitalmodel | structural | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-156 | FFS Phase 1 — wall thickness grid input with Level 1/2 accept-reject workflow | pending | high | complex | claude | digitalmodel | asset_integrity | ✅ | ✅ | ✅ | - | n/a | - |
| WRK-157 | Fatigue analysis module enhancement — S-N curve reporting and parametric sweeps | working | high | complex | claude | digitalmodel | fatigue | ✅ | ✅ | ✅ | ░░░ 40% | n/a | - |
| WRK-157 | Session locking — prevent WRK item collision across terminals | archived | high | moderate | claude | workspace-hub | - | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-158 | Wall thickness parametric engine — Cartesian sweep across D/t, pressure, material | archived | medium | medium | claude | digitalmodel | structural | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-159 | Three-way design code comparison report — API RP 1111 vs RP 2RD vs STD 2RD | archived | medium | medium | claude | digitalmodel | structural | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-160 | OSHA severe injury + fatality data completion and severity mapping fix | archived | medium | simple | claude | worldenergydata | hse | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-161 | BSEE Excel statistics re-download and URL importer verification | archived | medium | simple | claude | worldenergydata | hse | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-163 | Well planning risk empowerment framework | pending | medium | complex | claude | worldenergydata, digitalmodel | risk_assessment | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-164 | Well production test data quality and nodal analysis foundation | pending | high | complex | claude | worldenergydata, digitalmodel | production_engineering | ✅ | ✅ | ✅ | - | n/a | - |
| WRK-165 | Research subsea intervention analysis opportunities | pending | medium | medium | claude | digitalmodel, worldenergydata | subsea_intervention | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-166 | Jabra USB dongle lost — research universal dongle compatibility | pending | medium | simple | gemini | - | - | ✅ | ❌ | ❌ | - | n/a | - |
| WRK-167 | Calendar: Krishna ADHD evaluation — 24 Feb 2:30 PM | pending | high | simple | claude | - | - | ✅ | ❌ | ✅ | - | n/a | - |
| WRK-168 | MPD systems knowledge module — pressure management for drillships | pending | high | complex | claude | worldenergydata, digitalmodel | drilling_pressure_management | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-169 | Drilling technology evolution — MPD adoption case study | pending | medium | medium | claude | aceengineer-website, worldenergydata | content | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-173 | Session Management Workflow Documentation + Schematic | pending | high | low | claude | workspace-hub | - | ✅ | ❌ | ❌ | - | - | - |
| WRK-175 | Session Start: Engineering Context Loader | pending | medium | medium | claude+gemini | workspace-hub | - | ❌ | ❌ | ❌ | - | - | - |
| WRK-176 | Session Start: Design Code Version Guard | pending | high | low | codex | workspace-hub, digitalmodel | - | ❌ | ❌ | ❌ | - | - | - |
| WRK-177 | Stop Hook: Engineering Calculation Audit Trail | pending | high | medium | claude+codex | workspace-hub, worldenergydata | - | ❌ | ❌ | ❌ | - | - | - |
| WRK-178 | Stop Hook: Data Provenance Snapshot | pending | medium | medium | codex | workspace-hub, worldenergydata | - | ❌ | ❌ | ❌ | - | - | - |
| WRK-179 | Start Hook: Agent Capacity Pre-flight | pending | medium | low | codex | workspace-hub | - | ❌ | ❌ | ❌ | - | - | - |
| WRK-180 | Stop Hook: Cross-Agent Learning Sync | pending | low | high | claude+gemini | workspace-hub | - | ❌ | ❌ | ❌ | - | - | - |
| WRK-181 | Session Replay & Time Travel | pending | low | high | claude | workspace-hub | - | ❌ | ❌ | ❌ | - | - | - |
| WRK-182 | Predictive Session Planning | pending | low | high | claude+gemini | workspace-hub | - | ❌ | ❌ | ❌ | - | - | - |
| WRK-183 | Domain Knowledge Graph | pending | medium | high | claude+gemini | workspace-hub, worldenergydata, digitalmodel | - | ❌ | ❌ | ❌ | - | - | - |
| WRK-185 | Ecosystem Truth Review: instruction/skills/work-item centralization | archived | high | medium | codex+claude | workspace-hub, digitalmodel, worldenergydata | governance | ✅ | ✅ | ❌ | ███ 100% | n/a | - |
| WRK-188 | Wave-1 spec migration: worldenergydata dry-run manifest and apply plan | done | high | medium | codex+claude | workspace-hub, worldenergydata | governance | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-190 | NCS production data module — NPD/Sodir open data integration (worldenergydata) | pending | medium | moderate | codex | worldenergydata | ncs | ✅ | ❌ | ❌ | - | - | - |
| WRK-191 | Field development case study catalog — structured reference library of real projects | pending | medium | moderate | gemini | digitalmodel | field_development_references | ✅ | ❌ | ❌ | - | - | - |
| WRK-192 | Field development schematic generator — Python SVG/PNG layout diagrams | pending | medium | complex | codex | digitalmodel | field_development_visuals | ❌ | ❌ | ❌ | - | - | - |
| WRK-193 | UKCS production data module — NSTA/OPRED open data integration (worldenergydata) | pending | low | moderate | codex | worldenergydata | ukcs | ✅ | ❌ | ❌ | - | - | WRK-190 |
| WRK-194 | Brazil ANP production data module — well-level monthly CSV integration (worldenergydata) | pending | high | moderate | codex | worldenergydata | brazil_anp | ❌ | ❌ | ❌ | - | - | - |
| WRK-195 | EIA US production data module — non-GoM onshore + Alaska integration (worldenergydata) | pending | medium | moderate | codex | worldenergydata | eia_us | ❌ | ❌ | ❌ | - | - | - |
| WRK-196 | Canada offshore + emerging basin watch list (C-NLOER NL data; Guyana/Suriname/Namibia/Falklands monitor) | pending | low | moderate | codex | worldenergydata, digitalmodel | canada_offshore + emerging_basins | ❌ | ❌ | ❌ | - | - | WRK-190 |
| WRK-197 | Nigeria NUPRC + EITI data framework — West Africa deepwater and multi-country payment data | pending | low | moderate | codex | worldenergydata | west_africa | ❌ | ❌ | ❌ | - | - | - |

## By Status

### Done (unarchived)

| ID | Title | Priority | Complexity | Repos | Module |
|-----|-------|----------|------------|-------|--------|
| WRK-188 | Wave-1 spec migration: worldenergydata dry-run manifest and apply plan | high | medium | workspace-hub, worldenergydata | governance |

### Pending

| ID | Title | Priority | Complexity | Repos | Module |
|-----|-------|----------|------------|-------|--------|
| WRK-005 | Clean up email using AI (when safe) | low | medium | achantas-data | - |
| WRK-008 | Upload photos from multiple devices to achantas-media | low | medium | achantas-data | - |
| WRK-015 | Metocean data extrapolation to target locations using GIS and nearest-source modeling | medium | complex | worldenergydata | - |
| WRK-018 | Extend BSEE field data pipeline to other regulatory sources (RRC, Norway, Mexico, Brazil) | low | complex | worldenergydata | - |
| WRK-019 | Establish drilling, completion, and intervention cost data by region and environment | low | complex | worldenergydata | - |
| WRK-020 | GIS skill for cross-application geospatial tools — Blender, QGIS, well plotting | medium | complex | digitalmodel | - |
| WRK-021 | Stock analysis for drastic trend changes, technical indicators, and insider trading benchmarks | medium | complex | assethold | - |
| WRK-022 | US property valuation analysis using GIS — location, traffic, and spatial factors | medium | complex | assethold | - |
| WRK-023 | Property GIS development timeline with future projection and Google Earth animation | low | complex | assethold | - |
| WRK-032 | Modular OrcaFlex pipeline installation input with parametric campaign support | medium | complex | digitalmodel | - |
| WRK-036 | OrcaFlex structure deployment analysis - supply boat side deployment with structural loads | low | complex | acma-projects | - |
| WRK-039 | SPM project benchmarking - AQWA vs OrcaFlex | medium | complex | digitalmodel | - |
| WRK-041 | Develop long-term plan for Hobbies repo | low | medium | hobbies | - |
| WRK-042 | Develop long-term plan for Investments repo | low | medium | investments | - |
| WRK-043 | Parametric hull form analysis with RAO generation and client-facing lookup graphs | low | complex | digitalmodel | - |
| WRK-045 | OrcaFlex rigid jumper analysis - stress and VIV for various configurations | medium | complex | digitalmodel | - |
| WRK-046 | OrcaFlex drilling and completion riser parametric analysis | medium | complex | digitalmodel | - |
| WRK-047 | OpenFOAM CFD analysis capability for digitalmodel | low | complex | digitalmodel | - |
| WRK-048 | Blender working configurations for digitalmodel | low | medium | digitalmodel | - |
| WRK-050 | Hardware consolidation — inventory, assess, repurpose devices + dev environment readiness | medium | complex | workspace-hub | - |
| WRK-075 | OFFPIPE Integration Module — pipelay cross-validation against OrcaFlex | low | complex | digitalmodel | - |
| WRK-076 | Add data collection scheduler/orchestrator for automated refresh pipelines | medium | complex | worldenergydata | - |
| WRK-080 | Write 4 energy data blog posts for SEO | low | complex | aceengineer-website | - |
| WRK-081 | Build interactive NPV calculator for website lead generation | low | complex | aceengineer-website | - |
| WRK-084 | Integrate metocean data sources into unified aggregation interface | medium | complex | worldenergydata | - |
| WRK-085 | Create public sample data access page on website | low | medium | aceengineer-website | - |
| WRK-099 | Run 3-way benchmark on Unit Box hull | medium | medium | digitalmodel | - |
| WRK-101 | Add mesh decimation/coarsening to mesh-utilities skill | low | medium | digitalmodel | - |
| WRK-106 | Hull panel geometry generator from waterline, section, and profile line definitions | medium | complex | digitalmodel | - |
| WRK-111 | BSEE field development interactive map and analytics | medium | complex | worldenergydata, aceengineer-website | - |
| WRK-112 | Appliance lifecycle analytics module for assethold | medium | complex | assethold | - |
| WRK-118 | AI agent utilization strategy — leverage Claude, Codex, Gemini for planning, development, testing workflows | medium | complex | workspace-hub | - |
| WRK-126 | Benchmark all example models across time domain and frequency domain with seed equivalence | high | complex | digitalmodel | - |
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | high | complex | digitalmodel | - |
| WRK-137 | Download and parse rig spec PDFs (102 PDFs from 4 operators) | low | complex | worldenergydata | - |
| WRK-140 | Integrate gmsh meshing skill into digitalmodel and solver pipelines | medium | medium | digitalmodel, workspace-hub | - |
| WRK-141 | Create Achantas family tree to connect all family members | medium | medium | achantas-data | - |
| WRK-146 | Overhaul aceengineer-website: fix positioning, narrative, and social proof | high | complex | aceengineer-website | - |
| WRK-147 | Set up aceengineer-strategy private repo with business operations framework | high | complex | aceengineer-strategy | - |
| WRK-148 | ACE-GTM: A&CE Go-to-Market strategy stream | high | complex | aceengineer-website, aceengineer-strategy, workspace-hub | - |
| WRK-150 | assetutilities test coverage improvement (re-creates WRK-052) | medium | medium | assetutilities | - |
| WRK-151 | worldenergydata test coverage improvement (re-creates WRK-054) | medium | medium | worldenergydata | - |
| WRK-152 | Marine safety importer validation — verify MAIB/TSB/IMO/EMSA importers against real data | high | medium | worldenergydata | marine_safety |
| WRK-153 | Energy data case study — BSEE field economics with NPV/IRR workflow | medium | medium | aceengineer-website | - |
| WRK-154 | CI workflow rewrite — fix 2 GitHub Actions workflows | high | medium | workspace-hub | - |
| WRK-155 | DNV-ST-F101 submarine pipeline wall thickness — WSD and LRFD methods | high | complex | digitalmodel | structural |
| WRK-156 | FFS Phase 1 — wall thickness grid input with Level 1/2 accept-reject workflow | high | complex | digitalmodel | asset_integrity |
| WRK-163 | Well planning risk empowerment framework | medium | complex | worldenergydata, digitalmodel | risk_assessment |
| WRK-164 | Well production test data quality and nodal analysis foundation | high | complex | worldenergydata, digitalmodel | production_engineering |
| WRK-165 | Research subsea intervention analysis opportunities | medium | medium | digitalmodel, worldenergydata | subsea_intervention |
| WRK-166 | Jabra USB dongle lost — research universal dongle compatibility | medium | simple | - | - |
| WRK-167 | Calendar: Krishna ADHD evaluation — 24 Feb 2:30 PM | high | simple | - | - |
| WRK-168 | MPD systems knowledge module — pressure management for drillships | high | complex | worldenergydata, digitalmodel | drilling_pressure_management |
| WRK-169 | Drilling technology evolution — MPD adoption case study | medium | medium | aceengineer-website, worldenergydata | content |
| WRK-173 | Session Management Workflow Documentation + Schematic | high | low | workspace-hub | - |
| WRK-175 | Session Start: Engineering Context Loader | medium | medium | workspace-hub | - |
| WRK-176 | Session Start: Design Code Version Guard | high | low | workspace-hub, digitalmodel | - |
| WRK-177 | Stop Hook: Engineering Calculation Audit Trail | high | medium | workspace-hub, worldenergydata | - |
| WRK-178 | Stop Hook: Data Provenance Snapshot | medium | medium | workspace-hub, worldenergydata | - |
| WRK-179 | Start Hook: Agent Capacity Pre-flight | medium | low | workspace-hub | - |
| WRK-180 | Stop Hook: Cross-Agent Learning Sync | low | high | workspace-hub | - |
| WRK-181 | Session Replay & Time Travel | low | high | workspace-hub | - |
| WRK-182 | Predictive Session Planning | low | high | workspace-hub | - |
| WRK-183 | Domain Knowledge Graph | medium | high | workspace-hub, worldenergydata, digitalmodel | - |
| WRK-190 | NCS production data module — NPD/Sodir open data integration (worldenergydata) | medium | moderate | worldenergydata | ncs |
| WRK-191 | Field development case study catalog — structured reference library of real projects | medium | moderate | digitalmodel | field_development_references |
| WRK-192 | Field development schematic generator — Python SVG/PNG layout diagrams | medium | complex | digitalmodel | field_development_visuals |
| WRK-193 | UKCS production data module — NSTA/OPRED open data integration (worldenergydata) | low | moderate | worldenergydata | ukcs |
| WRK-194 | Brazil ANP production data module — well-level monthly CSV integration (worldenergydata) | high | moderate | worldenergydata | brazil_anp |
| WRK-195 | EIA US production data module — non-GoM onshore + Alaska integration (worldenergydata) | medium | moderate | worldenergydata | eia_us |
| WRK-196 | Canada offshore + emerging basin watch list (C-NLOER NL data; Guyana/Suriname/Namibia/Falklands monitor) | low | moderate | worldenergydata, digitalmodel | canada_offshore + emerging_basins |
| WRK-197 | Nigeria NUPRC + EITI data framework — West Africa deepwater and multi-country payment data | low | moderate | worldenergydata | west_africa |

### Working

| ID | Title | Priority | Complexity | Repos | Module |
|-----|-------|----------|------------|-------|--------|
| WRK-121 | Extract & Catalog OrcaFlex Models from rock-oil-field/s7 | high | medium | - | - |
| WRK-125 | OrcaFlex module roadmap — evolving coordination and progress tracking | high | low | digitalmodel | - |
| WRK-131 | Passing ship analysis for moored vessels — AQWA-based force calculation and mooring response | high | complex | digitalmodel | - |
| WRK-149 | digitalmodel test coverage improvement (re-creates WRK-051) | high | complex | digitalmodel | - |
| WRK-157 | Fatigue analysis module enhancement — S-N curve reporting and parametric sweeps | high | complex | digitalmodel | fatigue |

### Blocked

| ID | Title | Priority | Complexity | Repos | Module |
|-----|-------|----------|------------|-------|--------|
| WRK-006 | Upload videos from iPhone to YouTube | low | simple | achantas-data | - |
| WRK-064 | OrcaFlex format converter: license-required validation and backward-compat wrapper | medium | medium | digitalmodel | - |
| WRK-069 | Acquire USCG MISLE bulk dataset | high | simple | worldenergydata | - |

### Archived

| ID | Title | Priority | Complexity | Repos | Module |
|-----|-------|----------|------------|-------|--------|
| WRK-001 | Repair sink faucet in powder room at 11511 Piping Rock | medium | simple | achantas-data | - |
| WRK-002 | Stove repair with factory service at 11511 Piping Rock | medium | simple | achantas-data | - |
| WRK-003 | Garage clean up | medium | simple | achantas-data | - |
| WRK-004 | Reorganize storage in upstairs bathroom at 11511 Piping Rock | medium | simple | achantas-data | - |
| WRK-007 | Upload videos from Doris computer to YouTube | medium | simple | achantas-data | - |
| WRK-009 | Reproduce rev30 lower tertiary BSEE field results for repeatability | high | medium | worldenergydata | - |
| WRK-010 | Rerun lower tertiary analysis with latest BSEE data and validate | high | medium | worldenergydata | - |
| WRK-011 | Run BSEE analysis for all leases with field nicknames and geological era grouping | high | complex | worldenergydata | - |
| WRK-012 | Audit HSE public data coverage and identify gaps | high | medium | worldenergydata | - |
| WRK-013 | HSE data analysis to identify typical mishaps by activity and subactivity | high | complex | worldenergydata | - |
| WRK-014 | HSE risk index — client-facing risk insights with risk scoring | medium | complex | worldenergydata | - |
| WRK-016 | BSEE completion and intervention activity analysis for insights | medium | complex | worldenergydata | - |
| WRK-017 | Streamline BSEE field data analysis pipeline — wellbore, casing, drilling, completions, interventions | high | complex | worldenergydata | - |
| WRK-024 | Buckskin field BSEE data analysis — Keathley Canyon blocks 785, 828, 829, 830, 871, 872 | high | medium | worldenergydata | - |
| WRK-025 | AQWA diffraction analysis runner | high | complex | digitalmodel | - |
| WRK-026 | Unified input data format converter for diffraction solvers (AQWA, OrcaWave, BEMRosetta) | high | complex | digitalmodel | - |
| WRK-027 | AQWA batch analysis execution | high | medium | digitalmodel | - |
| WRK-028 | AQWA postprocessing - RAOs and verification | high | complex | digitalmodel | - |
| WRK-029 | OrcaWave diffraction analysis runner + file preparation | high | complex | digitalmodel | - |
| WRK-030 | OrcaWave batch analysis + postprocessing | high | complex | digitalmodel | - |
| WRK-031 | Benchmark OrcaWave vs AQWA for 2-3 hulls | medium | complex | digitalmodel | - |
| WRK-033 | Develop OrcaFlex include-file modular skill for parametrised analysis input | medium | complex | digitalmodel | - |
| WRK-034 | Develop OrcaWave modular file prep skill for parametrised analysis input | medium | complex | digitalmodel | - |
| WRK-035 | Develop AQWA modular file prep skill for parametrised analysis input | medium | complex | digitalmodel | - |
| WRK-037 | Get OrcaFlex framework of agreement and terms | medium | simple | aceengineer-admin | - |
| WRK-038 | Compile global LNG terminal project dataset with comprehensive parameters | medium | complex | worldenergydata | - |
| WRK-040 | Mooring benchmarking - AQWA vs OrcaFlex | medium | complex | digitalmodel | - |
| WRK-044 | Pipeline wall thickness calculations with parametric utilisation analysis | medium | complex | digitalmodel | - |
| WRK-049 | Determine dynacard module way forward | medium | medium | digitalmodel | - |
| WRK-051 | digitalmodel test coverage improvement | high | complex | digitalmodel | - |
| WRK-052 | assetutilities test coverage improvement | high | complex | assetutilities | - |
| WRK-053 | assethold test coverage improvement | medium | medium | assethold | - |
| WRK-054 | worldenergydata test coverage improvement | medium | medium | worldenergydata | - |
| WRK-055 | aceengineer-website test coverage improvement | low | simple | aceengineer-website | - |
| WRK-056 | aceengineer-admin test coverage improvement | medium | medium | aceengineer-admin | - |
| WRK-057 | Define canonical spec.yml schema for diffraction analysis | high | medium | digitalmodel | - |
| WRK-058 | AQWA input backend — spec.yml to single .dat and modular deck files | high | complex | digitalmodel | - |
| WRK-059 | OrcaWave input backend — spec.yml to single .yml and modular includes | high | complex | digitalmodel | - |
| WRK-060 | Common mesh format and converter pipeline (BEMRosetta + GMSH) | high | medium | digitalmodel | - |
| WRK-061 | CLI and integration layer for spec converter | medium | medium | digitalmodel | - |
| WRK-062 | Test suite for spec converter using existing example data | high | medium | digitalmodel | - |
| WRK-063 | Reverse parsers — AQWA .dat and OrcaWave .yml to canonical spec.yml | high | complex | digitalmodel | - |
| WRK-065 | S-lay pipeline installation schema + builders for PRPP Eclipse vessel | high | complex | digitalmodel | - |
| WRK-066 | Review and improve digitalmodel module structure for discoverability | high | complex | digitalmodel | - |
| WRK-067 | Acquire OSHA enforcement and fatality data | high | simple | worldenergydata | - |
| WRK-068 | Acquire BSEE incident investigations and INCs data | high | medium | worldenergydata | - |
| WRK-070 | Import PHMSA pipeline data and build pipeline_safety module | high | medium | worldenergydata | - |
| WRK-071 | Acquire NTSB CAROL marine investigations and EPA TRI data | high | simple | worldenergydata | - |
| WRK-072 | Technical safety analysis module for worldenergydata using ENIGMA theory | high | complex | worldenergydata | - |
| WRK-073 | Market digitalmodel and worldenergydata capabilities on aceengineer website | high | complex | aceengineer-website | - |
| WRK-074 | Complete marine safety database importers (MAIB, IMO, EMSA, TSB) | high | complex | worldenergydata | - |
| WRK-077 | Validate and wire decline curve modeling into BSEE production workflow | high | medium | worldenergydata | - |
| WRK-078 | Create energy data case study — BSEE field economics with NPV/IRR workflow | medium | medium | aceengineer-website | - |
| WRK-079 | Create marine safety case study — cross-database incident correlation | medium | medium | aceengineer-website | - |
| WRK-082 | Complete LNG terminal data pipeline — from config to working collection | medium | medium | worldenergydata | - |
| WRK-083 | Validate multi-format export (Excel, PDF, Parquet) with real BSEE data | medium | medium | worldenergydata | - |
| WRK-086 | Rewrite CI workflows for Python/bash workspace | medium | medium | workspace-hub | - |
| WRK-087 | Improve test coverage across workspace repos | high | complex | workspace-hub | - |
| WRK-088 | Investigate and clean submodule issues (pdf-large-reader, worldenergydata, aceengineercode) | low | simple | workspace-hub | - |
| WRK-089 | Review Claude Code version gap and update cc-insights | low | simple | workspace-hub | - |
| WRK-090 | Identify and refactor large files exceeding 400-line limit | medium | medium | workspace-hub | - |
| WRK-091 | Add dynacard module README | low | low | digitalmodel | - |
| WRK-092 | Register dynacard CLI entry point | low | low | digitalmodel | - |
| WRK-093 | Improve dynacard AI diagnostics | low | complex | digitalmodel | - |
| WRK-094 | Plan, reassess, and improve the workspace-hub workflow | high | complex | workspace-hub | - |
| WRK-096 | Review and improve worldenergydata module structure for discoverability | high | medium | worldenergydata | - |
| WRK-097 | Implement three-tier data residence strategy (worldenergydata ↔ digitalmodel) | high | medium | workspace-hub, worldenergydata, digitalmodel | - |
| WRK-098 | Clean up 7.1GB large data committed to worldenergydata git history | high | high | worldenergydata | - |
| WRK-100 | Run 3-way benchmark on Barge hull | medium | medium | digitalmodel | - |
| WRK-102 | Add generic hull definition/data for all rigs in worldenergydata | medium | medium | worldenergydata | - |
| WRK-103 | Add heavy construction/installation vessel data to worldenergydata | medium | medium | worldenergydata | - |
| WRK-104 | Expand drilling rig fleet dataset to all offshore and onshore rigs | high | complex | worldenergydata | - |
| WRK-105 | Add drilling riser component data to worldenergydata | medium | medium | worldenergydata | - |
| WRK-107 | Clarify Family Dollar 1099-MISC rent amount discrepancy ($50,085.60) | high | simple | sabithaandkrishnaestates | - |
| WRK-108 | Agent usage credits display — show remaining quota at session start for weekly planning | medium | medium | workspace-hub | - |
| WRK-109 | Review, refine, and curate hooks + skills — research best practices from existing workflows | medium | medium | workspace-hub, worldenergydata, digitalmodel | - |
| WRK-110 | Expand hull size library with FST, LNGC, and OrcaFlex benchmark shapes | medium | complex | digitalmodel | - |
| WRK-113 | Maintain always-current data index with freshness tracking and source metadata | high | medium | worldenergydata | - |
| WRK-114 | Collect hull panel shapes and sizes for various floating bodies from existing sources | medium | complex | digitalmodel, worldenergydata | - |
| WRK-115 | Link RAO data to hull shapes in hull library catalog | medium | medium | digitalmodel | - |
| WRK-116 | Scale hull panel meshes to target principal dimensions for hydrodynamic analysis | medium | medium | digitalmodel | - |
| WRK-117 | Refine and coarsen hull panel meshes for mesh convergence sensitivity analysis | medium | complex | digitalmodel | - |
| WRK-119 | Test suite optimization — tiered test profiles for commit, task, and session workflows | high | complex | workspace-hub, worldenergydata, digitalmodel | - |
| WRK-120 | Research and purchase a smart watch | low | simple | achantas-data | - |
| WRK-122 | Licensed Software Usage Workflow & Burden Reduction | high | medium | acma-projects, assetutilities | - |
| WRK-124 | Session 20260211_095832 — 1 file(s) created | medium | low | digitalmodel | - |
| WRK-127 | Sanitize and categorize ideal spec.yml templates for OrcaFlex input across structure types | high | medium | digitalmodel | - |
| WRK-132 | Refine OrcaWave benchmarks: barge/ship/spar RAO fixes + damping/gyradii/Km comparison | high | medium | digitalmodel | - |
| WRK-134 | Add future-work brainstorming step before archiving completed items | medium | medium | workspace-hub | - |
| WRK-135 | Ingest XLS historical rig fleet data (163 deepwater rigs) | medium | medium | worldenergydata | - |
| WRK-138 | Fitness-for-service module enhancement: wall thickness grid, industry targeting, and asset lifecycle | medium | complex | digitalmodel | asset_integrity |
| WRK-139 | Develop gmsh skill and documentation | medium | medium | workspace-hub | - |
| WRK-139 | Unified multi-agent orchestration architecture (Claude/Codex/Gemini) | high | complex | workspace-hub | agents |
| WRK-142 | Review work accomplishments and draft Anthropic outreach message | high | medium | workspace-hub | - |
| WRK-143 | Full symmetric M-T envelope — closed polygon lens shapes | medium | simple | digitalmodel | - |
| WRK-144 | API RP 2RD + API STD 2RD riser wall thickness — WSD & LRFD combined loading | medium | complex | digitalmodel | - |
| WRK-145 | Design code versioning — handle changing revisions of standards | medium | medium | digitalmodel | - |
| WRK-157 | Session locking — prevent WRK item collision across terminals | high | moderate | workspace-hub | - |
| WRK-158 | Wall thickness parametric engine — Cartesian sweep across D/t, pressure, material | medium | medium | digitalmodel | structural |
| WRK-159 | Three-way design code comparison report — API RP 1111 vs RP 2RD vs STD 2RD | medium | medium | digitalmodel | structural |
| WRK-160 | OSHA severe injury + fatality data completion and severity mapping fix | medium | simple | worldenergydata | hse |
| WRK-161 | BSEE Excel statistics re-download and URL importer verification | medium | simple | worldenergydata | hse |
| WRK-185 | Ecosystem Truth Review: instruction/skills/work-item centralization | high | medium | workspace-hub, digitalmodel, worldenergydata | governance |

## By Repository

### aceengineer-admin

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-037 | Get OrcaFlex framework of agreement and terms | archived | medium | simple | - |
| WRK-056 | aceengineer-admin test coverage improvement | archived | medium | medium | - |
| WRK-133 | Update OrcaFlex license agreement with addresses and 3rd-party terms | on-hold | high | medium | - |

### aceengineer-strategy

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-147 | Set up aceengineer-strategy private repo with business operations framework | pending | high | complex | - |
| WRK-148 | ACE-GTM: A&CE Go-to-Market strategy stream | pending | high | complex | - |

### aceengineer-website

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-055 | aceengineer-website test coverage improvement | archived | low | simple | - |
| WRK-073 | Market digitalmodel and worldenergydata capabilities on aceengineer website | archived | high | complex | - |
| WRK-078 | Create energy data case study — BSEE field economics with NPV/IRR workflow | archived | medium | medium | - |
| WRK-079 | Create marine safety case study — cross-database incident correlation | archived | medium | medium | - |
| WRK-080 | Write 4 energy data blog posts for SEO | pending | low | complex | - |
| WRK-081 | Build interactive NPV calculator for website lead generation | pending | low | complex | - |
| WRK-085 | Create public sample data access page on website | pending | low | medium | - |
| WRK-111 | BSEE field development interactive map and analytics | pending | medium | complex | - |
| WRK-146 | Overhaul aceengineer-website: fix positioning, narrative, and social proof | pending | high | complex | - |
| WRK-148 | ACE-GTM: A&CE Go-to-Market strategy stream | pending | high | complex | - |
| WRK-153 | Energy data case study — BSEE field economics with NPV/IRR workflow | pending | medium | medium | - |
| WRK-169 | Drilling technology evolution — MPD adoption case study | pending | medium | medium | content |

### achantas-data

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-001 | Repair sink faucet in powder room at 11511 Piping Rock | archived | medium | simple | - |
| WRK-002 | Stove repair with factory service at 11511 Piping Rock | archived | medium | simple | - |
| WRK-003 | Garage clean up | archived | medium | simple | - |
| WRK-004 | Reorganize storage in upstairs bathroom at 11511 Piping Rock | archived | medium | simple | - |
| WRK-005 | Clean up email using AI (when safe) | pending | low | medium | - |
| WRK-006 | Upload videos from iPhone to YouTube | blocked | low | simple | - |
| WRK-007 | Upload videos from Doris computer to YouTube | archived | medium | simple | - |
| WRK-008 | Upload photos from multiple devices to achantas-media | pending | low | medium | - |
| WRK-120 | Research and purchase a smart watch | archived | low | simple | - |
| WRK-141 | Create Achantas family tree to connect all family members | pending | medium | medium | - |

### acma-projects

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-036 | OrcaFlex structure deployment analysis - supply boat side deployment with structural loads | pending | low | complex | - |
| WRK-122 | Licensed Software Usage Workflow & Burden Reduction | archived | high | medium | - |

### assethold

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-021 | Stock analysis for drastic trend changes, technical indicators, and insider trading benchmarks | pending | medium | complex | - |
| WRK-022 | US property valuation analysis using GIS — location, traffic, and spatial factors | pending | medium | complex | - |
| WRK-023 | Property GIS development timeline with future projection and Google Earth animation | pending | low | complex | - |
| WRK-053 | assethold test coverage improvement | archived | medium | medium | - |
| WRK-112 | Appliance lifecycle analytics module for assethold | pending | medium | complex | - |

### assetutilities

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-052 | assetutilities test coverage improvement | archived | high | complex | - |
| WRK-122 | Licensed Software Usage Workflow & Burden Reduction | archived | high | medium | - |
| WRK-150 | assetutilities test coverage improvement (re-creates WRK-052) | pending | medium | medium | - |

### digitalmodel

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-020 | GIS skill for cross-application geospatial tools — Blender, QGIS, well plotting | pending | medium | complex | - |
| WRK-025 | AQWA diffraction analysis runner | archived | high | complex | - |
| WRK-026 | Unified input data format converter for diffraction solvers (AQWA, OrcaWave, BEMRosetta) | archived | high | complex | - |
| WRK-027 | AQWA batch analysis execution | archived | high | medium | - |
| WRK-028 | AQWA postprocessing - RAOs and verification | archived | high | complex | - |
| WRK-029 | OrcaWave diffraction analysis runner + file preparation | archived | high | complex | - |
| WRK-030 | OrcaWave batch analysis + postprocessing | archived | high | complex | - |
| WRK-031 | Benchmark OrcaWave vs AQWA for 2-3 hulls | archived | medium | complex | - |
| WRK-032 | Modular OrcaFlex pipeline installation input with parametric campaign support | pending | medium | complex | - |
| WRK-033 | Develop OrcaFlex include-file modular skill for parametrised analysis input | archived | medium | complex | - |
| WRK-034 | Develop OrcaWave modular file prep skill for parametrised analysis input | archived | medium | complex | - |
| WRK-035 | Develop AQWA modular file prep skill for parametrised analysis input | archived | medium | complex | - |
| WRK-039 | SPM project benchmarking - AQWA vs OrcaFlex | pending | medium | complex | - |
| WRK-040 | Mooring benchmarking - AQWA vs OrcaFlex | archived | medium | complex | - |
| WRK-043 | Parametric hull form analysis with RAO generation and client-facing lookup graphs | pending | low | complex | - |
| WRK-044 | Pipeline wall thickness calculations with parametric utilisation analysis | archived | medium | complex | - |
| WRK-045 | OrcaFlex rigid jumper analysis - stress and VIV for various configurations | pending | medium | complex | - |
| WRK-046 | OrcaFlex drilling and completion riser parametric analysis | pending | medium | complex | - |
| WRK-047 | OpenFOAM CFD analysis capability for digitalmodel | pending | low | complex | - |
| WRK-048 | Blender working configurations for digitalmodel | pending | low | medium | - |
| WRK-049 | Determine dynacard module way forward | archived | medium | medium | - |
| WRK-051 | digitalmodel test coverage improvement | archived | high | complex | - |
| WRK-057 | Define canonical spec.yml schema for diffraction analysis | archived | high | medium | - |
| WRK-058 | AQWA input backend — spec.yml to single .dat and modular deck files | archived | high | complex | - |
| WRK-059 | OrcaWave input backend — spec.yml to single .yml and modular includes | archived | high | complex | - |
| WRK-060 | Common mesh format and converter pipeline (BEMRosetta + GMSH) | archived | high | medium | - |
| WRK-061 | CLI and integration layer for spec converter | archived | medium | medium | - |
| WRK-062 | Test suite for spec converter using existing example data | archived | high | medium | - |
| WRK-063 | Reverse parsers — AQWA .dat and OrcaWave .yml to canonical spec.yml | archived | high | complex | - |
| WRK-064 | OrcaFlex format converter: license-required validation and backward-compat wrapper | blocked | medium | medium | - |
| WRK-065 | S-lay pipeline installation schema + builders for PRPP Eclipse vessel | archived | high | complex | - |
| WRK-066 | Review and improve digitalmodel module structure for discoverability | archived | high | complex | - |
| WRK-075 | OFFPIPE Integration Module — pipelay cross-validation against OrcaFlex | pending | low | complex | - |
| WRK-091 | Add dynacard module README | archived | low | low | - |
| WRK-092 | Register dynacard CLI entry point | archived | low | low | - |
| WRK-093 | Improve dynacard AI diagnostics | archived | low | complex | - |
| WRK-097 | Implement three-tier data residence strategy (worldenergydata ↔ digitalmodel) | archived | high | medium | - |
| WRK-099 | Run 3-way benchmark on Unit Box hull | pending | medium | medium | - |
| WRK-100 | Run 3-way benchmark on Barge hull | archived | medium | medium | - |
| WRK-101 | Add mesh decimation/coarsening to mesh-utilities skill | pending | low | medium | - |
| WRK-106 | Hull panel geometry generator from waterline, section, and profile line definitions | pending | medium | complex | - |
| WRK-109 | Review, refine, and curate hooks + skills — research best practices from existing workflows | archived | medium | medium | - |
| WRK-110 | Expand hull size library with FST, LNGC, and OrcaFlex benchmark shapes | archived | medium | complex | - |
| WRK-114 | Collect hull panel shapes and sizes for various floating bodies from existing sources | archived | medium | complex | - |
| WRK-115 | Link RAO data to hull shapes in hull library catalog | archived | medium | medium | - |
| WRK-116 | Scale hull panel meshes to target principal dimensions for hydrodynamic analysis | archived | medium | medium | - |
| WRK-117 | Refine and coarsen hull panel meshes for mesh convergence sensitivity analysis | archived | medium | complex | - |
| WRK-119 | Test suite optimization — tiered test profiles for commit, task, and session workflows | archived | high | complex | - |
| WRK-124 | Session 20260211_095832 — 1 file(s) created | archived | medium | low | - |
| WRK-125 | OrcaFlex module roadmap — evolving coordination and progress tracking | working | high | low | - |
| WRK-126 | Benchmark all example models across time domain and frequency domain with seed equivalence | pending | high | complex | - |
| WRK-127 | Sanitize and categorize ideal spec.yml templates for OrcaFlex input across structure types | archived | high | medium | - |
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | pending | high | complex | - |
| WRK-130 | Standardize analysis reporting for each OrcaWave structure type | on-hold | high | complex | - |
| WRK-131 | Passing ship analysis for moored vessels — AQWA-based force calculation and mooring response | working | high | complex | - |
| WRK-132 | Refine OrcaWave benchmarks: barge/ship/spar RAO fixes + damping/gyradii/Km comparison | archived | high | medium | - |
| WRK-138 | Fitness-for-service module enhancement: wall thickness grid, industry targeting, and asset lifecycle | archived | medium | complex | asset_integrity |
| WRK-140 | Integrate gmsh meshing skill into digitalmodel and solver pipelines | pending | medium | medium | - |
| WRK-143 | Full symmetric M-T envelope — closed polygon lens shapes | archived | medium | simple | - |
| WRK-144 | API RP 2RD + API STD 2RD riser wall thickness — WSD & LRFD combined loading | archived | medium | complex | - |
| WRK-145 | Design code versioning — handle changing revisions of standards | archived | medium | medium | - |
| WRK-149 | digitalmodel test coverage improvement (re-creates WRK-051) | working | high | complex | - |
| WRK-155 | DNV-ST-F101 submarine pipeline wall thickness — WSD and LRFD methods | pending | high | complex | structural |
| WRK-156 | FFS Phase 1 — wall thickness grid input with Level 1/2 accept-reject workflow | pending | high | complex | asset_integrity |
| WRK-157 | Fatigue analysis module enhancement — S-N curve reporting and parametric sweeps | working | high | complex | fatigue |
| WRK-158 | Wall thickness parametric engine — Cartesian sweep across D/t, pressure, material | archived | medium | medium | structural |
| WRK-159 | Three-way design code comparison report — API RP 1111 vs RP 2RD vs STD 2RD | archived | medium | medium | structural |
| WRK-163 | Well planning risk empowerment framework | pending | medium | complex | risk_assessment |
| WRK-164 | Well production test data quality and nodal analysis foundation | pending | high | complex | production_engineering |
| WRK-165 | Research subsea intervention analysis opportunities | pending | medium | medium | subsea_intervention |
| WRK-168 | MPD systems knowledge module — pressure management for drillships | pending | high | complex | drilling_pressure_management |
| WRK-176 | Session Start: Design Code Version Guard | pending | high | low | - |
| WRK-183 | Domain Knowledge Graph | pending | medium | high | - |
| WRK-185 | Ecosystem Truth Review: instruction/skills/work-item centralization | archived | high | medium | governance |
| WRK-191 | Field development case study catalog — structured reference library of real projects | pending | medium | moderate | field_development_references |
| WRK-192 | Field development schematic generator — Python SVG/PNG layout diagrams | pending | medium | complex | field_development_visuals |
| WRK-196 | Canada offshore + emerging basin watch list (C-NLOER NL data; Guyana/Suriname/Namibia/Falklands monitor) | pending | low | moderate | canada_offshore + emerging_basins |

### hobbies

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-041 | Develop long-term plan for Hobbies repo | pending | low | medium | - |

### investments

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-042 | Develop long-term plan for Investments repo | pending | low | medium | - |

### sabithaandkrishnaestates

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-107 | Clarify Family Dollar 1099-MISC rent amount discrepancy ($50,085.60) | archived | high | simple | - |

### workspace-hub

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-050 | Hardware consolidation — inventory, assess, repurpose devices + dev environment readiness | pending | medium | complex | - |
| WRK-086 | Rewrite CI workflows for Python/bash workspace | archived | medium | medium | - |
| WRK-087 | Improve test coverage across workspace repos | archived | high | complex | - |
| WRK-088 | Investigate and clean submodule issues (pdf-large-reader, worldenergydata, aceengineercode) | archived | low | simple | - |
| WRK-089 | Review Claude Code version gap and update cc-insights | archived | low | simple | - |
| WRK-090 | Identify and refactor large files exceeding 400-line limit | archived | medium | medium | - |
| WRK-094 | Plan, reassess, and improve the workspace-hub workflow | archived | high | complex | - |
| WRK-097 | Implement three-tier data residence strategy (worldenergydata ↔ digitalmodel) | archived | high | medium | - |
| WRK-108 | Agent usage credits display — show remaining quota at session start for weekly planning | archived | medium | medium | - |
| WRK-109 | Review, refine, and curate hooks + skills — research best practices from existing workflows | archived | medium | medium | - |
| WRK-118 | AI agent utilization strategy — leverage Claude, Codex, Gemini for planning, development, testing workflows | pending | medium | complex | - |
| WRK-119 | Test suite optimization — tiered test profiles for commit, task, and session workflows | archived | high | complex | - |
| WRK-134 | Add future-work brainstorming step before archiving completed items | archived | medium | medium | - |
| WRK-139 | Develop gmsh skill and documentation | archived | medium | medium | - |
| WRK-139 | Unified multi-agent orchestration architecture (Claude/Codex/Gemini) | archived | high | complex | agents |
| WRK-140 | Integrate gmsh meshing skill into digitalmodel and solver pipelines | pending | medium | medium | - |
| WRK-142 | Review work accomplishments and draft Anthropic outreach message | archived | high | medium | - |
| WRK-148 | ACE-GTM: A&CE Go-to-Market strategy stream | pending | high | complex | - |
| WRK-154 | CI workflow rewrite — fix 2 GitHub Actions workflows | pending | high | medium | - |
| WRK-157 | Session locking — prevent WRK item collision across terminals | archived | high | moderate | - |
| WRK-173 | Session Management Workflow Documentation + Schematic | pending | high | low | - |
| WRK-175 | Session Start: Engineering Context Loader | pending | medium | medium | - |
| WRK-176 | Session Start: Design Code Version Guard | pending | high | low | - |
| WRK-177 | Stop Hook: Engineering Calculation Audit Trail | pending | high | medium | - |
| WRK-178 | Stop Hook: Data Provenance Snapshot | pending | medium | medium | - |
| WRK-179 | Start Hook: Agent Capacity Pre-flight | pending | medium | low | - |
| WRK-180 | Stop Hook: Cross-Agent Learning Sync | pending | low | high | - |
| WRK-181 | Session Replay & Time Travel | pending | low | high | - |
| WRK-182 | Predictive Session Planning | pending | low | high | - |
| WRK-183 | Domain Knowledge Graph | pending | medium | high | - |
| WRK-185 | Ecosystem Truth Review: instruction/skills/work-item centralization | archived | high | medium | governance |
| WRK-188 | Wave-1 spec migration: worldenergydata dry-run manifest and apply plan | done | high | medium | governance |

### worldenergydata

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-009 | Reproduce rev30 lower tertiary BSEE field results for repeatability | archived | high | medium | - |
| WRK-010 | Rerun lower tertiary analysis with latest BSEE data and validate | archived | high | medium | - |
| WRK-011 | Run BSEE analysis for all leases with field nicknames and geological era grouping | archived | high | complex | - |
| WRK-012 | Audit HSE public data coverage and identify gaps | archived | high | medium | - |
| WRK-013 | HSE data analysis to identify typical mishaps by activity and subactivity | archived | high | complex | - |
| WRK-014 | HSE risk index — client-facing risk insights with risk scoring | archived | medium | complex | - |
| WRK-015 | Metocean data extrapolation to target locations using GIS and nearest-source modeling | pending | medium | complex | - |
| WRK-016 | BSEE completion and intervention activity analysis for insights | archived | medium | complex | - |
| WRK-017 | Streamline BSEE field data analysis pipeline — wellbore, casing, drilling, completions, interventions | archived | high | complex | - |
| WRK-018 | Extend BSEE field data pipeline to other regulatory sources (RRC, Norway, Mexico, Brazil) | pending | low | complex | - |
| WRK-019 | Establish drilling, completion, and intervention cost data by region and environment | pending | low | complex | - |
| WRK-024 | Buckskin field BSEE data analysis — Keathley Canyon blocks 785, 828, 829, 830, 871, 872 | archived | high | medium | - |
| WRK-038 | Compile global LNG terminal project dataset with comprehensive parameters | archived | medium | complex | - |
| WRK-054 | worldenergydata test coverage improvement | archived | medium | medium | - |
| WRK-067 | Acquire OSHA enforcement and fatality data | archived | high | simple | - |
| WRK-068 | Acquire BSEE incident investigations and INCs data | archived | high | medium | - |
| WRK-069 | Acquire USCG MISLE bulk dataset | blocked | high | simple | - |
| WRK-070 | Import PHMSA pipeline data and build pipeline_safety module | archived | high | medium | - |
| WRK-071 | Acquire NTSB CAROL marine investigations and EPA TRI data | archived | high | simple | - |
| WRK-072 | Technical safety analysis module for worldenergydata using ENIGMA theory | archived | high | complex | - |
| WRK-074 | Complete marine safety database importers (MAIB, IMO, EMSA, TSB) | archived | high | complex | - |
| WRK-076 | Add data collection scheduler/orchestrator for automated refresh pipelines | pending | medium | complex | - |
| WRK-077 | Validate and wire decline curve modeling into BSEE production workflow | archived | high | medium | - |
| WRK-082 | Complete LNG terminal data pipeline — from config to working collection | archived | medium | medium | - |
| WRK-083 | Validate multi-format export (Excel, PDF, Parquet) with real BSEE data | archived | medium | medium | - |
| WRK-084 | Integrate metocean data sources into unified aggregation interface | pending | medium | complex | - |
| WRK-096 | Review and improve worldenergydata module structure for discoverability | archived | high | medium | - |
| WRK-097 | Implement three-tier data residence strategy (worldenergydata ↔ digitalmodel) | archived | high | medium | - |
| WRK-098 | Clean up 7.1GB large data committed to worldenergydata git history | archived | high | high | - |
| WRK-102 | Add generic hull definition/data for all rigs in worldenergydata | archived | medium | medium | - |
| WRK-103 | Add heavy construction/installation vessel data to worldenergydata | archived | medium | medium | - |
| WRK-104 | Expand drilling rig fleet dataset to all offshore and onshore rigs | archived | high | complex | - |
| WRK-105 | Add drilling riser component data to worldenergydata | archived | medium | medium | - |
| WRK-109 | Review, refine, and curate hooks + skills — research best practices from existing workflows | archived | medium | medium | - |
| WRK-111 | BSEE field development interactive map and analytics | pending | medium | complex | - |
| WRK-113 | Maintain always-current data index with freshness tracking and source metadata | archived | high | medium | - |
| WRK-114 | Collect hull panel shapes and sizes for various floating bodies from existing sources | archived | medium | complex | - |
| WRK-119 | Test suite optimization — tiered test profiles for commit, task, and session workflows | archived | high | complex | - |
| WRK-135 | Ingest XLS historical rig fleet data (163 deepwater rigs) | archived | medium | medium | - |
| WRK-137 | Download and parse rig spec PDFs (102 PDFs from 4 operators) | pending | low | complex | - |
| WRK-151 | worldenergydata test coverage improvement (re-creates WRK-054) | pending | medium | medium | - |
| WRK-152 | Marine safety importer validation — verify MAIB/TSB/IMO/EMSA importers against real data | pending | high | medium | marine_safety |
| WRK-160 | OSHA severe injury + fatality data completion and severity mapping fix | archived | medium | simple | hse |
| WRK-161 | BSEE Excel statistics re-download and URL importer verification | archived | medium | simple | hse |
| WRK-163 | Well planning risk empowerment framework | pending | medium | complex | risk_assessment |
| WRK-164 | Well production test data quality and nodal analysis foundation | pending | high | complex | production_engineering |
| WRK-165 | Research subsea intervention analysis opportunities | pending | medium | medium | subsea_intervention |
| WRK-168 | MPD systems knowledge module — pressure management for drillships | pending | high | complex | drilling_pressure_management |
| WRK-169 | Drilling technology evolution — MPD adoption case study | pending | medium | medium | content |
| WRK-177 | Stop Hook: Engineering Calculation Audit Trail | pending | high | medium | - |
| WRK-178 | Stop Hook: Data Provenance Snapshot | pending | medium | medium | - |
| WRK-183 | Domain Knowledge Graph | pending | medium | high | - |
| WRK-185 | Ecosystem Truth Review: instruction/skills/work-item centralization | archived | high | medium | governance |
| WRK-188 | Wave-1 spec migration: worldenergydata dry-run manifest and apply plan | done | high | medium | governance |
| WRK-190 | NCS production data module — NPD/Sodir open data integration (worldenergydata) | pending | medium | moderate | ncs |
| WRK-193 | UKCS production data module — NSTA/OPRED open data integration (worldenergydata) | pending | low | moderate | ukcs |
| WRK-194 | Brazil ANP production data module — well-level monthly CSV integration (worldenergydata) | pending | high | moderate | brazil_anp |
| WRK-195 | EIA US production data module — non-GoM onshore + Alaska integration (worldenergydata) | pending | medium | moderate | eia_us |
| WRK-196 | Canada offshore + emerging basin watch list (C-NLOER NL data; Guyana/Suriname/Namibia/Falklands monitor) | pending | low | moderate | canada_offshore + emerging_basins |
| WRK-197 | Nigeria NUPRC + EITI data framework — West Africa deepwater and multi-country payment data | pending | low | moderate | west_africa |

## By Priority

### High

| ID | Title | Status | Complexity | Repos | Module |
|-----|-------|--------|------------|-------|--------|
| WRK-009 | Reproduce rev30 lower tertiary BSEE field results for repeatability | archived | medium | worldenergydata | - |
| WRK-010 | Rerun lower tertiary analysis with latest BSEE data and validate | archived | medium | worldenergydata | - |
| WRK-011 | Run BSEE analysis for all leases with field nicknames and geological era grouping | archived | complex | worldenergydata | - |
| WRK-012 | Audit HSE public data coverage and identify gaps | archived | medium | worldenergydata | - |
| WRK-013 | HSE data analysis to identify typical mishaps by activity and subactivity | archived | complex | worldenergydata | - |
| WRK-017 | Streamline BSEE field data analysis pipeline — wellbore, casing, drilling, completions, interventions | archived | complex | worldenergydata | - |
| WRK-024 | Buckskin field BSEE data analysis — Keathley Canyon blocks 785, 828, 829, 830, 871, 872 | archived | medium | worldenergydata | - |
| WRK-025 | AQWA diffraction analysis runner | archived | complex | digitalmodel | - |
| WRK-026 | Unified input data format converter for diffraction solvers (AQWA, OrcaWave, BEMRosetta) | archived | complex | digitalmodel | - |
| WRK-027 | AQWA batch analysis execution | archived | medium | digitalmodel | - |
| WRK-028 | AQWA postprocessing - RAOs and verification | archived | complex | digitalmodel | - |
| WRK-029 | OrcaWave diffraction analysis runner + file preparation | archived | complex | digitalmodel | - |
| WRK-030 | OrcaWave batch analysis + postprocessing | archived | complex | digitalmodel | - |
| WRK-051 | digitalmodel test coverage improvement | archived | complex | digitalmodel | - |
| WRK-052 | assetutilities test coverage improvement | archived | complex | assetutilities | - |
| WRK-057 | Define canonical spec.yml schema for diffraction analysis | archived | medium | digitalmodel | - |
| WRK-058 | AQWA input backend — spec.yml to single .dat and modular deck files | archived | complex | digitalmodel | - |
| WRK-059 | OrcaWave input backend — spec.yml to single .yml and modular includes | archived | complex | digitalmodel | - |
| WRK-060 | Common mesh format and converter pipeline (BEMRosetta + GMSH) | archived | medium | digitalmodel | - |
| WRK-062 | Test suite for spec converter using existing example data | archived | medium | digitalmodel | - |
| WRK-063 | Reverse parsers — AQWA .dat and OrcaWave .yml to canonical spec.yml | archived | complex | digitalmodel | - |
| WRK-065 | S-lay pipeline installation schema + builders for PRPP Eclipse vessel | archived | complex | digitalmodel | - |
| WRK-066 | Review and improve digitalmodel module structure for discoverability | archived | complex | digitalmodel | - |
| WRK-067 | Acquire OSHA enforcement and fatality data | archived | simple | worldenergydata | - |
| WRK-068 | Acquire BSEE incident investigations and INCs data | archived | medium | worldenergydata | - |
| WRK-069 | Acquire USCG MISLE bulk dataset | blocked | simple | worldenergydata | - |
| WRK-070 | Import PHMSA pipeline data and build pipeline_safety module | archived | medium | worldenergydata | - |
| WRK-071 | Acquire NTSB CAROL marine investigations and EPA TRI data | archived | simple | worldenergydata | - |
| WRK-072 | Technical safety analysis module for worldenergydata using ENIGMA theory | archived | complex | worldenergydata | - |
| WRK-073 | Market digitalmodel and worldenergydata capabilities on aceengineer website | archived | complex | aceengineer-website | - |
| WRK-074 | Complete marine safety database importers (MAIB, IMO, EMSA, TSB) | archived | complex | worldenergydata | - |
| WRK-077 | Validate and wire decline curve modeling into BSEE production workflow | archived | medium | worldenergydata | - |
| WRK-087 | Improve test coverage across workspace repos | archived | complex | workspace-hub | - |
| WRK-094 | Plan, reassess, and improve the workspace-hub workflow | archived | complex | workspace-hub | - |
| WRK-096 | Review and improve worldenergydata module structure for discoverability | archived | medium | worldenergydata | - |
| WRK-097 | Implement three-tier data residence strategy (worldenergydata ↔ digitalmodel) | archived | medium | workspace-hub, worldenergydata, digitalmodel | - |
| WRK-098 | Clean up 7.1GB large data committed to worldenergydata git history | archived | high | worldenergydata | - |
| WRK-104 | Expand drilling rig fleet dataset to all offshore and onshore rigs | archived | complex | worldenergydata | - |
| WRK-107 | Clarify Family Dollar 1099-MISC rent amount discrepancy ($50,085.60) | archived | simple | sabithaandkrishnaestates | - |
| WRK-113 | Maintain always-current data index with freshness tracking and source metadata | archived | medium | worldenergydata | - |
| WRK-119 | Test suite optimization — tiered test profiles for commit, task, and session workflows | archived | complex | workspace-hub, worldenergydata, digitalmodel | - |
| WRK-121 | Extract & Catalog OrcaFlex Models from rock-oil-field/s7 | working | medium | - | - |
| WRK-122 | Licensed Software Usage Workflow & Burden Reduction | archived | medium | acma-projects, assetutilities | - |
| WRK-125 | OrcaFlex module roadmap — evolving coordination and progress tracking | working | low | digitalmodel | - |
| WRK-126 | Benchmark all example models across time domain and frequency domain with seed equivalence | pending | complex | digitalmodel | - |
| WRK-127 | Sanitize and categorize ideal spec.yml templates for OrcaFlex input across structure types | archived | medium | digitalmodel | - |
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | pending | complex | digitalmodel | - |
| WRK-130 | Standardize analysis reporting for each OrcaWave structure type | on-hold | complex | digitalmodel | - |
| WRK-131 | Passing ship analysis for moored vessels — AQWA-based force calculation and mooring response | working | complex | digitalmodel | - |
| WRK-132 | Refine OrcaWave benchmarks: barge/ship/spar RAO fixes + damping/gyradii/Km comparison | archived | medium | digitalmodel | - |
| WRK-133 | Update OrcaFlex license agreement with addresses and 3rd-party terms | on-hold | medium | aceengineer-admin | - |
| WRK-139 | Unified multi-agent orchestration architecture (Claude/Codex/Gemini) | archived | complex | workspace-hub | agents |
| WRK-142 | Review work accomplishments and draft Anthropic outreach message | archived | medium | workspace-hub | - |
| WRK-146 | Overhaul aceengineer-website: fix positioning, narrative, and social proof | pending | complex | aceengineer-website | - |
| WRK-147 | Set up aceengineer-strategy private repo with business operations framework | pending | complex | aceengineer-strategy | - |
| WRK-148 | ACE-GTM: A&CE Go-to-Market strategy stream | pending | complex | aceengineer-website, aceengineer-strategy, workspace-hub | - |
| WRK-149 | digitalmodel test coverage improvement (re-creates WRK-051) | working | complex | digitalmodel | - |
| WRK-152 | Marine safety importer validation — verify MAIB/TSB/IMO/EMSA importers against real data | pending | medium | worldenergydata | marine_safety |
| WRK-154 | CI workflow rewrite — fix 2 GitHub Actions workflows | pending | medium | workspace-hub | - |
| WRK-155 | DNV-ST-F101 submarine pipeline wall thickness — WSD and LRFD methods | pending | complex | digitalmodel | structural |
| WRK-156 | FFS Phase 1 — wall thickness grid input with Level 1/2 accept-reject workflow | pending | complex | digitalmodel | asset_integrity |
| WRK-157 | Fatigue analysis module enhancement — S-N curve reporting and parametric sweeps | working | complex | digitalmodel | fatigue |
| WRK-157 | Session locking — prevent WRK item collision across terminals | archived | moderate | workspace-hub | - |
| WRK-164 | Well production test data quality and nodal analysis foundation | pending | complex | worldenergydata, digitalmodel | production_engineering |
| WRK-167 | Calendar: Krishna ADHD evaluation — 24 Feb 2:30 PM | pending | simple | - | - |
| WRK-168 | MPD systems knowledge module — pressure management for drillships | pending | complex | worldenergydata, digitalmodel | drilling_pressure_management |
| WRK-173 | Session Management Workflow Documentation + Schematic | pending | low | workspace-hub | - |
| WRK-176 | Session Start: Design Code Version Guard | pending | low | workspace-hub, digitalmodel | - |
| WRK-177 | Stop Hook: Engineering Calculation Audit Trail | pending | medium | workspace-hub, worldenergydata | - |
| WRK-185 | Ecosystem Truth Review: instruction/skills/work-item centralization | archived | medium | workspace-hub, digitalmodel, worldenergydata | governance |
| WRK-188 | Wave-1 spec migration: worldenergydata dry-run manifest and apply plan | done | medium | workspace-hub, worldenergydata | governance |
| WRK-194 | Brazil ANP production data module — well-level monthly CSV integration (worldenergydata) | pending | moderate | worldenergydata | brazil_anp |

### Medium

| ID | Title | Status | Complexity | Repos | Module |
|-----|-------|--------|------------|-------|--------|
| WRK-001 | Repair sink faucet in powder room at 11511 Piping Rock | archived | simple | achantas-data | - |
| WRK-002 | Stove repair with factory service at 11511 Piping Rock | archived | simple | achantas-data | - |
| WRK-003 | Garage clean up | archived | simple | achantas-data | - |
| WRK-004 | Reorganize storage in upstairs bathroom at 11511 Piping Rock | archived | simple | achantas-data | - |
| WRK-007 | Upload videos from Doris computer to YouTube | archived | simple | achantas-data | - |
| WRK-014 | HSE risk index — client-facing risk insights with risk scoring | archived | complex | worldenergydata | - |
| WRK-015 | Metocean data extrapolation to target locations using GIS and nearest-source modeling | pending | complex | worldenergydata | - |
| WRK-016 | BSEE completion and intervention activity analysis for insights | archived | complex | worldenergydata | - |
| WRK-020 | GIS skill for cross-application geospatial tools — Blender, QGIS, well plotting | pending | complex | digitalmodel | - |
| WRK-021 | Stock analysis for drastic trend changes, technical indicators, and insider trading benchmarks | pending | complex | assethold | - |
| WRK-022 | US property valuation analysis using GIS — location, traffic, and spatial factors | pending | complex | assethold | - |
| WRK-031 | Benchmark OrcaWave vs AQWA for 2-3 hulls | archived | complex | digitalmodel | - |
| WRK-032 | Modular OrcaFlex pipeline installation input with parametric campaign support | pending | complex | digitalmodel | - |
| WRK-033 | Develop OrcaFlex include-file modular skill for parametrised analysis input | archived | complex | digitalmodel | - |
| WRK-034 | Develop OrcaWave modular file prep skill for parametrised analysis input | archived | complex | digitalmodel | - |
| WRK-035 | Develop AQWA modular file prep skill for parametrised analysis input | archived | complex | digitalmodel | - |
| WRK-037 | Get OrcaFlex framework of agreement and terms | archived | simple | aceengineer-admin | - |
| WRK-038 | Compile global LNG terminal project dataset with comprehensive parameters | archived | complex | worldenergydata | - |
| WRK-039 | SPM project benchmarking - AQWA vs OrcaFlex | pending | complex | digitalmodel | - |
| WRK-040 | Mooring benchmarking - AQWA vs OrcaFlex | archived | complex | digitalmodel | - |
| WRK-044 | Pipeline wall thickness calculations with parametric utilisation analysis | archived | complex | digitalmodel | - |
| WRK-045 | OrcaFlex rigid jumper analysis - stress and VIV for various configurations | pending | complex | digitalmodel | - |
| WRK-046 | OrcaFlex drilling and completion riser parametric analysis | pending | complex | digitalmodel | - |
| WRK-049 | Determine dynacard module way forward | archived | medium | digitalmodel | - |
| WRK-050 | Hardware consolidation — inventory, assess, repurpose devices + dev environment readiness | pending | complex | workspace-hub | - |
| WRK-053 | assethold test coverage improvement | archived | medium | assethold | - |
| WRK-054 | worldenergydata test coverage improvement | archived | medium | worldenergydata | - |
| WRK-056 | aceengineer-admin test coverage improvement | archived | medium | aceengineer-admin | - |
| WRK-061 | CLI and integration layer for spec converter | archived | medium | digitalmodel | - |
| WRK-064 | OrcaFlex format converter: license-required validation and backward-compat wrapper | blocked | medium | digitalmodel | - |
| WRK-076 | Add data collection scheduler/orchestrator for automated refresh pipelines | pending | complex | worldenergydata | - |
| WRK-078 | Create energy data case study — BSEE field economics with NPV/IRR workflow | archived | medium | aceengineer-website | - |
| WRK-079 | Create marine safety case study — cross-database incident correlation | archived | medium | aceengineer-website | - |
| WRK-082 | Complete LNG terminal data pipeline — from config to working collection | archived | medium | worldenergydata | - |
| WRK-083 | Validate multi-format export (Excel, PDF, Parquet) with real BSEE data | archived | medium | worldenergydata | - |
| WRK-084 | Integrate metocean data sources into unified aggregation interface | pending | complex | worldenergydata | - |
| WRK-086 | Rewrite CI workflows for Python/bash workspace | archived | medium | workspace-hub | - |
| WRK-090 | Identify and refactor large files exceeding 400-line limit | archived | medium | workspace-hub | - |
| WRK-099 | Run 3-way benchmark on Unit Box hull | pending | medium | digitalmodel | - |
| WRK-100 | Run 3-way benchmark on Barge hull | archived | medium | digitalmodel | - |
| WRK-102 | Add generic hull definition/data for all rigs in worldenergydata | archived | medium | worldenergydata | - |
| WRK-103 | Add heavy construction/installation vessel data to worldenergydata | archived | medium | worldenergydata | - |
| WRK-105 | Add drilling riser component data to worldenergydata | archived | medium | worldenergydata | - |
| WRK-106 | Hull panel geometry generator from waterline, section, and profile line definitions | pending | complex | digitalmodel | - |
| WRK-108 | Agent usage credits display — show remaining quota at session start for weekly planning | archived | medium | workspace-hub | - |
| WRK-109 | Review, refine, and curate hooks + skills — research best practices from existing workflows | archived | medium | workspace-hub, worldenergydata, digitalmodel | - |
| WRK-110 | Expand hull size library with FST, LNGC, and OrcaFlex benchmark shapes | archived | complex | digitalmodel | - |
| WRK-111 | BSEE field development interactive map and analytics | pending | complex | worldenergydata, aceengineer-website | - |
| WRK-112 | Appliance lifecycle analytics module for assethold | pending | complex | assethold | - |
| WRK-114 | Collect hull panel shapes and sizes for various floating bodies from existing sources | archived | complex | digitalmodel, worldenergydata | - |
| WRK-115 | Link RAO data to hull shapes in hull library catalog | archived | medium | digitalmodel | - |
| WRK-116 | Scale hull panel meshes to target principal dimensions for hydrodynamic analysis | archived | medium | digitalmodel | - |
| WRK-117 | Refine and coarsen hull panel meshes for mesh convergence sensitivity analysis | archived | complex | digitalmodel | - |
| WRK-118 | AI agent utilization strategy — leverage Claude, Codex, Gemini for planning, development, testing workflows | pending | complex | workspace-hub | - |
| WRK-124 | Session 20260211_095832 — 1 file(s) created | archived | low | digitalmodel | - |
| WRK-134 | Add future-work brainstorming step before archiving completed items | archived | medium | workspace-hub | - |
| WRK-135 | Ingest XLS historical rig fleet data (163 deepwater rigs) | archived | medium | worldenergydata | - |
| WRK-138 | Fitness-for-service module enhancement: wall thickness grid, industry targeting, and asset lifecycle | archived | complex | digitalmodel | asset_integrity |
| WRK-139 | Develop gmsh skill and documentation | archived | medium | workspace-hub | - |
| WRK-140 | Integrate gmsh meshing skill into digitalmodel and solver pipelines | pending | medium | digitalmodel, workspace-hub | - |
| WRK-141 | Create Achantas family tree to connect all family members | pending | medium | achantas-data | - |
| WRK-143 | Full symmetric M-T envelope — closed polygon lens shapes | archived | simple | digitalmodel | - |
| WRK-144 | API RP 2RD + API STD 2RD riser wall thickness — WSD & LRFD combined loading | archived | complex | digitalmodel | - |
| WRK-145 | Design code versioning — handle changing revisions of standards | archived | medium | digitalmodel | - |
| WRK-150 | assetutilities test coverage improvement (re-creates WRK-052) | pending | medium | assetutilities | - |
| WRK-151 | worldenergydata test coverage improvement (re-creates WRK-054) | pending | medium | worldenergydata | - |
| WRK-153 | Energy data case study — BSEE field economics with NPV/IRR workflow | pending | medium | aceengineer-website | - |
| WRK-158 | Wall thickness parametric engine — Cartesian sweep across D/t, pressure, material | archived | medium | digitalmodel | structural |
| WRK-159 | Three-way design code comparison report — API RP 1111 vs RP 2RD vs STD 2RD | archived | medium | digitalmodel | structural |
| WRK-160 | OSHA severe injury + fatality data completion and severity mapping fix | archived | simple | worldenergydata | hse |
| WRK-161 | BSEE Excel statistics re-download and URL importer verification | archived | simple | worldenergydata | hse |
| WRK-163 | Well planning risk empowerment framework | pending | complex | worldenergydata, digitalmodel | risk_assessment |
| WRK-165 | Research subsea intervention analysis opportunities | pending | medium | digitalmodel, worldenergydata | subsea_intervention |
| WRK-166 | Jabra USB dongle lost — research universal dongle compatibility | pending | simple | - | - |
| WRK-169 | Drilling technology evolution — MPD adoption case study | pending | medium | aceengineer-website, worldenergydata | content |
| WRK-175 | Session Start: Engineering Context Loader | pending | medium | workspace-hub | - |
| WRK-178 | Stop Hook: Data Provenance Snapshot | pending | medium | workspace-hub, worldenergydata | - |
| WRK-179 | Start Hook: Agent Capacity Pre-flight | pending | low | workspace-hub | - |
| WRK-183 | Domain Knowledge Graph | pending | high | workspace-hub, worldenergydata, digitalmodel | - |
| WRK-190 | NCS production data module — NPD/Sodir open data integration (worldenergydata) | pending | moderate | worldenergydata | ncs |
| WRK-191 | Field development case study catalog — structured reference library of real projects | pending | moderate | digitalmodel | field_development_references |
| WRK-192 | Field development schematic generator — Python SVG/PNG layout diagrams | pending | complex | digitalmodel | field_development_visuals |
| WRK-195 | EIA US production data module — non-GoM onshore + Alaska integration (worldenergydata) | pending | moderate | worldenergydata | eia_us |

### Low

| ID | Title | Status | Complexity | Repos | Module |
|-----|-------|--------|------------|-------|--------|
| WRK-005 | Clean up email using AI (when safe) | pending | medium | achantas-data | - |
| WRK-006 | Upload videos from iPhone to YouTube | blocked | simple | achantas-data | - |
| WRK-008 | Upload photos from multiple devices to achantas-media | pending | medium | achantas-data | - |
| WRK-018 | Extend BSEE field data pipeline to other regulatory sources (RRC, Norway, Mexico, Brazil) | pending | complex | worldenergydata | - |
| WRK-019 | Establish drilling, completion, and intervention cost data by region and environment | pending | complex | worldenergydata | - |
| WRK-023 | Property GIS development timeline with future projection and Google Earth animation | pending | complex | assethold | - |
| WRK-036 | OrcaFlex structure deployment analysis - supply boat side deployment with structural loads | pending | complex | acma-projects | - |
| WRK-041 | Develop long-term plan for Hobbies repo | pending | medium | hobbies | - |
| WRK-042 | Develop long-term plan for Investments repo | pending | medium | investments | - |
| WRK-043 | Parametric hull form analysis with RAO generation and client-facing lookup graphs | pending | complex | digitalmodel | - |
| WRK-047 | OpenFOAM CFD analysis capability for digitalmodel | pending | complex | digitalmodel | - |
| WRK-048 | Blender working configurations for digitalmodel | pending | medium | digitalmodel | - |
| WRK-055 | aceengineer-website test coverage improvement | archived | simple | aceengineer-website | - |
| WRK-075 | OFFPIPE Integration Module — pipelay cross-validation against OrcaFlex | pending | complex | digitalmodel | - |
| WRK-080 | Write 4 energy data blog posts for SEO | pending | complex | aceengineer-website | - |
| WRK-081 | Build interactive NPV calculator for website lead generation | pending | complex | aceengineer-website | - |
| WRK-085 | Create public sample data access page on website | pending | medium | aceengineer-website | - |
| WRK-088 | Investigate and clean submodule issues (pdf-large-reader, worldenergydata, aceengineercode) | archived | simple | workspace-hub | - |
| WRK-089 | Review Claude Code version gap and update cc-insights | archived | simple | workspace-hub | - |
| WRK-091 | Add dynacard module README | archived | low | digitalmodel | - |
| WRK-092 | Register dynacard CLI entry point | archived | low | digitalmodel | - |
| WRK-093 | Improve dynacard AI diagnostics | archived | complex | digitalmodel | - |
| WRK-101 | Add mesh decimation/coarsening to mesh-utilities skill | pending | medium | digitalmodel | - |
| WRK-120 | Research and purchase a smart watch | archived | simple | achantas-data | - |
| WRK-137 | Download and parse rig spec PDFs (102 PDFs from 4 operators) | pending | complex | worldenergydata | - |
| WRK-180 | Stop Hook: Cross-Agent Learning Sync | pending | high | workspace-hub | - |
| WRK-181 | Session Replay & Time Travel | pending | high | workspace-hub | - |
| WRK-182 | Predictive Session Planning | pending | high | workspace-hub | - |
| WRK-193 | UKCS production data module — NSTA/OPRED open data integration (worldenergydata) | pending | moderate | worldenergydata | ukcs |
| WRK-196 | Canada offshore + emerging basin watch list (C-NLOER NL data; Guyana/Suriname/Namibia/Falklands monitor) | pending | moderate | worldenergydata, digitalmodel | canada_offshore + emerging_basins |
| WRK-197 | Nigeria NUPRC + EITI data framework — West Africa deepwater and multi-country payment data | pending | moderate | worldenergydata | west_africa |

## By Complexity

### Simple

| ID | Title | Status | Priority | Repos | Module |
|-----|-------|--------|----------|-------|--------|
| WRK-001 | Repair sink faucet in powder room at 11511 Piping Rock | archived | medium | achantas-data | - |
| WRK-002 | Stove repair with factory service at 11511 Piping Rock | archived | medium | achantas-data | - |
| WRK-003 | Garage clean up | archived | medium | achantas-data | - |
| WRK-004 | Reorganize storage in upstairs bathroom at 11511 Piping Rock | archived | medium | achantas-data | - |
| WRK-006 | Upload videos from iPhone to YouTube | blocked | low | achantas-data | - |
| WRK-007 | Upload videos from Doris computer to YouTube | archived | medium | achantas-data | - |
| WRK-037 | Get OrcaFlex framework of agreement and terms | archived | medium | aceengineer-admin | - |
| WRK-055 | aceengineer-website test coverage improvement | archived | low | aceengineer-website | - |
| WRK-067 | Acquire OSHA enforcement and fatality data | archived | high | worldenergydata | - |
| WRK-069 | Acquire USCG MISLE bulk dataset | blocked | high | worldenergydata | - |
| WRK-071 | Acquire NTSB CAROL marine investigations and EPA TRI data | archived | high | worldenergydata | - |
| WRK-088 | Investigate and clean submodule issues (pdf-large-reader, worldenergydata, aceengineercode) | archived | low | workspace-hub | - |
| WRK-089 | Review Claude Code version gap and update cc-insights | archived | low | workspace-hub | - |
| WRK-107 | Clarify Family Dollar 1099-MISC rent amount discrepancy ($50,085.60) | archived | high | sabithaandkrishnaestates | - |
| WRK-120 | Research and purchase a smart watch | archived | low | achantas-data | - |
| WRK-143 | Full symmetric M-T envelope — closed polygon lens shapes | archived | medium | digitalmodel | - |
| WRK-160 | OSHA severe injury + fatality data completion and severity mapping fix | archived | medium | worldenergydata | hse |
| WRK-161 | BSEE Excel statistics re-download and URL importer verification | archived | medium | worldenergydata | hse |
| WRK-166 | Jabra USB dongle lost — research universal dongle compatibility | pending | medium | - | - |
| WRK-167 | Calendar: Krishna ADHD evaluation — 24 Feb 2:30 PM | pending | high | - | - |

### Medium

| ID | Title | Status | Priority | Repos | Module |
|-----|-------|--------|----------|-------|--------|
| WRK-005 | Clean up email using AI (when safe) | pending | low | achantas-data | - |
| WRK-008 | Upload photos from multiple devices to achantas-media | pending | low | achantas-data | - |
| WRK-009 | Reproduce rev30 lower tertiary BSEE field results for repeatability | archived | high | worldenergydata | - |
| WRK-010 | Rerun lower tertiary analysis with latest BSEE data and validate | archived | high | worldenergydata | - |
| WRK-012 | Audit HSE public data coverage and identify gaps | archived | high | worldenergydata | - |
| WRK-024 | Buckskin field BSEE data analysis — Keathley Canyon blocks 785, 828, 829, 830, 871, 872 | archived | high | worldenergydata | - |
| WRK-027 | AQWA batch analysis execution | archived | high | digitalmodel | - |
| WRK-041 | Develop long-term plan for Hobbies repo | pending | low | hobbies | - |
| WRK-042 | Develop long-term plan for Investments repo | pending | low | investments | - |
| WRK-048 | Blender working configurations for digitalmodel | pending | low | digitalmodel | - |
| WRK-049 | Determine dynacard module way forward | archived | medium | digitalmodel | - |
| WRK-053 | assethold test coverage improvement | archived | medium | assethold | - |
| WRK-054 | worldenergydata test coverage improvement | archived | medium | worldenergydata | - |
| WRK-056 | aceengineer-admin test coverage improvement | archived | medium | aceengineer-admin | - |
| WRK-057 | Define canonical spec.yml schema for diffraction analysis | archived | high | digitalmodel | - |
| WRK-060 | Common mesh format and converter pipeline (BEMRosetta + GMSH) | archived | high | digitalmodel | - |
| WRK-061 | CLI and integration layer for spec converter | archived | medium | digitalmodel | - |
| WRK-062 | Test suite for spec converter using existing example data | archived | high | digitalmodel | - |
| WRK-064 | OrcaFlex format converter: license-required validation and backward-compat wrapper | blocked | medium | digitalmodel | - |
| WRK-068 | Acquire BSEE incident investigations and INCs data | archived | high | worldenergydata | - |
| WRK-070 | Import PHMSA pipeline data and build pipeline_safety module | archived | high | worldenergydata | - |
| WRK-077 | Validate and wire decline curve modeling into BSEE production workflow | archived | high | worldenergydata | - |
| WRK-078 | Create energy data case study — BSEE field economics with NPV/IRR workflow | archived | medium | aceengineer-website | - |
| WRK-079 | Create marine safety case study — cross-database incident correlation | archived | medium | aceengineer-website | - |
| WRK-082 | Complete LNG terminal data pipeline — from config to working collection | archived | medium | worldenergydata | - |
| WRK-083 | Validate multi-format export (Excel, PDF, Parquet) with real BSEE data | archived | medium | worldenergydata | - |
| WRK-085 | Create public sample data access page on website | pending | low | aceengineer-website | - |
| WRK-086 | Rewrite CI workflows for Python/bash workspace | archived | medium | workspace-hub | - |
| WRK-090 | Identify and refactor large files exceeding 400-line limit | archived | medium | workspace-hub | - |
| WRK-096 | Review and improve worldenergydata module structure for discoverability | archived | high | worldenergydata | - |
| WRK-097 | Implement three-tier data residence strategy (worldenergydata ↔ digitalmodel) | archived | high | workspace-hub, worldenergydata, digitalmodel | - |
| WRK-099 | Run 3-way benchmark on Unit Box hull | pending | medium | digitalmodel | - |
| WRK-100 | Run 3-way benchmark on Barge hull | archived | medium | digitalmodel | - |
| WRK-101 | Add mesh decimation/coarsening to mesh-utilities skill | pending | low | digitalmodel | - |
| WRK-102 | Add generic hull definition/data for all rigs in worldenergydata | archived | medium | worldenergydata | - |
| WRK-103 | Add heavy construction/installation vessel data to worldenergydata | archived | medium | worldenergydata | - |
| WRK-105 | Add drilling riser component data to worldenergydata | archived | medium | worldenergydata | - |
| WRK-108 | Agent usage credits display — show remaining quota at session start for weekly planning | archived | medium | workspace-hub | - |
| WRK-109 | Review, refine, and curate hooks + skills — research best practices from existing workflows | archived | medium | workspace-hub, worldenergydata, digitalmodel | - |
| WRK-113 | Maintain always-current data index with freshness tracking and source metadata | archived | high | worldenergydata | - |
| WRK-115 | Link RAO data to hull shapes in hull library catalog | archived | medium | digitalmodel | - |
| WRK-116 | Scale hull panel meshes to target principal dimensions for hydrodynamic analysis | archived | medium | digitalmodel | - |
| WRK-121 | Extract & Catalog OrcaFlex Models from rock-oil-field/s7 | working | high | - | - |
| WRK-122 | Licensed Software Usage Workflow & Burden Reduction | archived | high | acma-projects, assetutilities | - |
| WRK-127 | Sanitize and categorize ideal spec.yml templates for OrcaFlex input across structure types | archived | high | digitalmodel | - |
| WRK-132 | Refine OrcaWave benchmarks: barge/ship/spar RAO fixes + damping/gyradii/Km comparison | archived | high | digitalmodel | - |
| WRK-133 | Update OrcaFlex license agreement with addresses and 3rd-party terms | on-hold | high | aceengineer-admin | - |
| WRK-134 | Add future-work brainstorming step before archiving completed items | archived | medium | workspace-hub | - |
| WRK-135 | Ingest XLS historical rig fleet data (163 deepwater rigs) | archived | medium | worldenergydata | - |
| WRK-139 | Develop gmsh skill and documentation | archived | medium | workspace-hub | - |
| WRK-140 | Integrate gmsh meshing skill into digitalmodel and solver pipelines | pending | medium | digitalmodel, workspace-hub | - |
| WRK-141 | Create Achantas family tree to connect all family members | pending | medium | achantas-data | - |
| WRK-142 | Review work accomplishments and draft Anthropic outreach message | archived | high | workspace-hub | - |
| WRK-145 | Design code versioning — handle changing revisions of standards | archived | medium | digitalmodel | - |
| WRK-150 | assetutilities test coverage improvement (re-creates WRK-052) | pending | medium | assetutilities | - |
| WRK-151 | worldenergydata test coverage improvement (re-creates WRK-054) | pending | medium | worldenergydata | - |
| WRK-152 | Marine safety importer validation — verify MAIB/TSB/IMO/EMSA importers against real data | pending | high | worldenergydata | marine_safety |
| WRK-153 | Energy data case study — BSEE field economics with NPV/IRR workflow | pending | medium | aceengineer-website | - |
| WRK-154 | CI workflow rewrite — fix 2 GitHub Actions workflows | pending | high | workspace-hub | - |
| WRK-158 | Wall thickness parametric engine — Cartesian sweep across D/t, pressure, material | archived | medium | digitalmodel | structural |
| WRK-159 | Three-way design code comparison report — API RP 1111 vs RP 2RD vs STD 2RD | archived | medium | digitalmodel | structural |
| WRK-165 | Research subsea intervention analysis opportunities | pending | medium | digitalmodel, worldenergydata | subsea_intervention |
| WRK-169 | Drilling technology evolution — MPD adoption case study | pending | medium | aceengineer-website, worldenergydata | content |
| WRK-175 | Session Start: Engineering Context Loader | pending | medium | workspace-hub | - |
| WRK-177 | Stop Hook: Engineering Calculation Audit Trail | pending | high | workspace-hub, worldenergydata | - |
| WRK-178 | Stop Hook: Data Provenance Snapshot | pending | medium | workspace-hub, worldenergydata | - |
| WRK-185 | Ecosystem Truth Review: instruction/skills/work-item centralization | archived | high | workspace-hub, digitalmodel, worldenergydata | governance |
| WRK-188 | Wave-1 spec migration: worldenergydata dry-run manifest and apply plan | done | high | workspace-hub, worldenergydata | governance |

### Complex

| ID | Title | Status | Priority | Repos | Module |
|-----|-------|--------|----------|-------|--------|
| WRK-011 | Run BSEE analysis for all leases with field nicknames and geological era grouping | archived | high | worldenergydata | - |
| WRK-013 | HSE data analysis to identify typical mishaps by activity and subactivity | archived | high | worldenergydata | - |
| WRK-014 | HSE risk index — client-facing risk insights with risk scoring | archived | medium | worldenergydata | - |
| WRK-015 | Metocean data extrapolation to target locations using GIS and nearest-source modeling | pending | medium | worldenergydata | - |
| WRK-016 | BSEE completion and intervention activity analysis for insights | archived | medium | worldenergydata | - |
| WRK-017 | Streamline BSEE field data analysis pipeline — wellbore, casing, drilling, completions, interventions | archived | high | worldenergydata | - |
| WRK-018 | Extend BSEE field data pipeline to other regulatory sources (RRC, Norway, Mexico, Brazil) | pending | low | worldenergydata | - |
| WRK-019 | Establish drilling, completion, and intervention cost data by region and environment | pending | low | worldenergydata | - |
| WRK-020 | GIS skill for cross-application geospatial tools — Blender, QGIS, well plotting | pending | medium | digitalmodel | - |
| WRK-021 | Stock analysis for drastic trend changes, technical indicators, and insider trading benchmarks | pending | medium | assethold | - |
| WRK-022 | US property valuation analysis using GIS — location, traffic, and spatial factors | pending | medium | assethold | - |
| WRK-023 | Property GIS development timeline with future projection and Google Earth animation | pending | low | assethold | - |
| WRK-025 | AQWA diffraction analysis runner | archived | high | digitalmodel | - |
| WRK-026 | Unified input data format converter for diffraction solvers (AQWA, OrcaWave, BEMRosetta) | archived | high | digitalmodel | - |
| WRK-028 | AQWA postprocessing - RAOs and verification | archived | high | digitalmodel | - |
| WRK-029 | OrcaWave diffraction analysis runner + file preparation | archived | high | digitalmodel | - |
| WRK-030 | OrcaWave batch analysis + postprocessing | archived | high | digitalmodel | - |
| WRK-031 | Benchmark OrcaWave vs AQWA for 2-3 hulls | archived | medium | digitalmodel | - |
| WRK-032 | Modular OrcaFlex pipeline installation input with parametric campaign support | pending | medium | digitalmodel | - |
| WRK-033 | Develop OrcaFlex include-file modular skill for parametrised analysis input | archived | medium | digitalmodel | - |
| WRK-034 | Develop OrcaWave modular file prep skill for parametrised analysis input | archived | medium | digitalmodel | - |
| WRK-035 | Develop AQWA modular file prep skill for parametrised analysis input | archived | medium | digitalmodel | - |
| WRK-036 | OrcaFlex structure deployment analysis - supply boat side deployment with structural loads | pending | low | acma-projects | - |
| WRK-038 | Compile global LNG terminal project dataset with comprehensive parameters | archived | medium | worldenergydata | - |
| WRK-039 | SPM project benchmarking - AQWA vs OrcaFlex | pending | medium | digitalmodel | - |
| WRK-040 | Mooring benchmarking - AQWA vs OrcaFlex | archived | medium | digitalmodel | - |
| WRK-043 | Parametric hull form analysis with RAO generation and client-facing lookup graphs | pending | low | digitalmodel | - |
| WRK-044 | Pipeline wall thickness calculations with parametric utilisation analysis | archived | medium | digitalmodel | - |
| WRK-045 | OrcaFlex rigid jumper analysis - stress and VIV for various configurations | pending | medium | digitalmodel | - |
| WRK-046 | OrcaFlex drilling and completion riser parametric analysis | pending | medium | digitalmodel | - |
| WRK-047 | OpenFOAM CFD analysis capability for digitalmodel | pending | low | digitalmodel | - |
| WRK-050 | Hardware consolidation — inventory, assess, repurpose devices + dev environment readiness | pending | medium | workspace-hub | - |
| WRK-051 | digitalmodel test coverage improvement | archived | high | digitalmodel | - |
| WRK-052 | assetutilities test coverage improvement | archived | high | assetutilities | - |
| WRK-058 | AQWA input backend — spec.yml to single .dat and modular deck files | archived | high | digitalmodel | - |
| WRK-059 | OrcaWave input backend — spec.yml to single .yml and modular includes | archived | high | digitalmodel | - |
| WRK-063 | Reverse parsers — AQWA .dat and OrcaWave .yml to canonical spec.yml | archived | high | digitalmodel | - |
| WRK-065 | S-lay pipeline installation schema + builders for PRPP Eclipse vessel | archived | high | digitalmodel | - |
| WRK-066 | Review and improve digitalmodel module structure for discoverability | archived | high | digitalmodel | - |
| WRK-072 | Technical safety analysis module for worldenergydata using ENIGMA theory | archived | high | worldenergydata | - |
| WRK-073 | Market digitalmodel and worldenergydata capabilities on aceengineer website | archived | high | aceengineer-website | - |
| WRK-074 | Complete marine safety database importers (MAIB, IMO, EMSA, TSB) | archived | high | worldenergydata | - |
| WRK-075 | OFFPIPE Integration Module — pipelay cross-validation against OrcaFlex | pending | low | digitalmodel | - |
| WRK-076 | Add data collection scheduler/orchestrator for automated refresh pipelines | pending | medium | worldenergydata | - |
| WRK-080 | Write 4 energy data blog posts for SEO | pending | low | aceengineer-website | - |
| WRK-081 | Build interactive NPV calculator for website lead generation | pending | low | aceengineer-website | - |
| WRK-084 | Integrate metocean data sources into unified aggregation interface | pending | medium | worldenergydata | - |
| WRK-087 | Improve test coverage across workspace repos | archived | high | workspace-hub | - |
| WRK-093 | Improve dynacard AI diagnostics | archived | low | digitalmodel | - |
| WRK-094 | Plan, reassess, and improve the workspace-hub workflow | archived | high | workspace-hub | - |
| WRK-104 | Expand drilling rig fleet dataset to all offshore and onshore rigs | archived | high | worldenergydata | - |
| WRK-106 | Hull panel geometry generator from waterline, section, and profile line definitions | pending | medium | digitalmodel | - |
| WRK-110 | Expand hull size library with FST, LNGC, and OrcaFlex benchmark shapes | archived | medium | digitalmodel | - |
| WRK-111 | BSEE field development interactive map and analytics | pending | medium | worldenergydata, aceengineer-website | - |
| WRK-112 | Appliance lifecycle analytics module for assethold | pending | medium | assethold | - |
| WRK-114 | Collect hull panel shapes and sizes for various floating bodies from existing sources | archived | medium | digitalmodel, worldenergydata | - |
| WRK-117 | Refine and coarsen hull panel meshes for mesh convergence sensitivity analysis | archived | medium | digitalmodel | - |
| WRK-118 | AI agent utilization strategy — leverage Claude, Codex, Gemini for planning, development, testing workflows | pending | medium | workspace-hub | - |
| WRK-119 | Test suite optimization — tiered test profiles for commit, task, and session workflows | archived | high | workspace-hub, worldenergydata, digitalmodel | - |
| WRK-126 | Benchmark all example models across time domain and frequency domain with seed equivalence | pending | high | digitalmodel | - |
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | pending | high | digitalmodel | - |
| WRK-130 | Standardize analysis reporting for each OrcaWave structure type | on-hold | high | digitalmodel | - |
| WRK-131 | Passing ship analysis for moored vessels — AQWA-based force calculation and mooring response | working | high | digitalmodel | - |
| WRK-137 | Download and parse rig spec PDFs (102 PDFs from 4 operators) | pending | low | worldenergydata | - |
| WRK-138 | Fitness-for-service module enhancement: wall thickness grid, industry targeting, and asset lifecycle | archived | medium | digitalmodel | asset_integrity |
| WRK-139 | Unified multi-agent orchestration architecture (Claude/Codex/Gemini) | archived | high | workspace-hub | agents |
| WRK-144 | API RP 2RD + API STD 2RD riser wall thickness — WSD & LRFD combined loading | archived | medium | digitalmodel | - |
| WRK-146 | Overhaul aceengineer-website: fix positioning, narrative, and social proof | pending | high | aceengineer-website | - |
| WRK-147 | Set up aceengineer-strategy private repo with business operations framework | pending | high | aceengineer-strategy | - |
| WRK-148 | ACE-GTM: A&CE Go-to-Market strategy stream | pending | high | aceengineer-website, aceengineer-strategy, workspace-hub | - |
| WRK-149 | digitalmodel test coverage improvement (re-creates WRK-051) | working | high | digitalmodel | - |
| WRK-155 | DNV-ST-F101 submarine pipeline wall thickness — WSD and LRFD methods | pending | high | digitalmodel | structural |
| WRK-156 | FFS Phase 1 — wall thickness grid input with Level 1/2 accept-reject workflow | pending | high | digitalmodel | asset_integrity |
| WRK-157 | Fatigue analysis module enhancement — S-N curve reporting and parametric sweeps | working | high | digitalmodel | fatigue |
| WRK-163 | Well planning risk empowerment framework | pending | medium | worldenergydata, digitalmodel | risk_assessment |
| WRK-164 | Well production test data quality and nodal analysis foundation | pending | high | worldenergydata, digitalmodel | production_engineering |
| WRK-168 | MPD systems knowledge module — pressure management for drillships | pending | high | worldenergydata, digitalmodel | drilling_pressure_management |
| WRK-192 | Field development schematic generator — Python SVG/PNG layout diagrams | pending | medium | digitalmodel | field_development_visuals |

## Dependencies

| ID | Title | Blocked By | Children | Parent |
|-----|-------|------------|----------|--------|
| WRK-010 | Rerun lower tertiary analysis with latest BSEE data and validate | WRK-009 | - | - |
| WRK-011 | Run BSEE analysis for all leases with field nicknames and geological era grouping | WRK-010 | - | - |
| WRK-013 | HSE data analysis to identify typical mishaps by activity and subactivity | WRK-012 | - | - |
| WRK-014 | HSE risk index — client-facing risk insights with risk scoring | WRK-013 | - | - |
| WRK-018 | Extend BSEE field data pipeline to other regulatory sources (RRC, Norway, Mexico, Brazil) | WRK-017 | - | - |
| WRK-019 | Establish drilling, completion, and intervention cost data by region and environment | WRK-017 | - | - |
| WRK-026 | Unified input data format converter for diffraction solvers (AQWA, OrcaWave, BEMRosetta) | - | WRK-057, WRK-058, WRK-059, WRK-060, WRK-061, WRK-062, WRK-063 | - |
| WRK-027 | AQWA batch analysis execution | WRK-025 | - | - |
| WRK-028 | AQWA postprocessing - RAOs and verification | WRK-025 | - | - |
| WRK-030 | OrcaWave batch analysis + postprocessing | WRK-029 | - | - |
| WRK-057 | Define canonical spec.yml schema for diffraction analysis | - | - | WRK-026 |
| WRK-058 | AQWA input backend — spec.yml to single .dat and modular deck files | WRK-057 | - | WRK-026 |
| WRK-059 | OrcaWave input backend — spec.yml to single .yml and modular includes | WRK-057 | - | WRK-026 |
| WRK-060 | Common mesh format and converter pipeline (BEMRosetta + GMSH) | - | - | WRK-026 |
| WRK-061 | CLI and integration layer for spec converter | WRK-058, WRK-059, WRK-060 | - | WRK-026 |
| WRK-062 | Test suite for spec converter using existing example data | WRK-057 | - | WRK-026 |
| WRK-063 | Reverse parsers — AQWA .dat and OrcaWave .yml to canonical spec.yml | WRK-057 | - | WRK-026 |
| WRK-079 | Create marine safety case study — cross-database incident correlation | WRK-074 | - | - |
| WRK-085 | Create public sample data access page on website | WRK-075 | - | - |
| WRK-100 | Run 3-way benchmark on Barge hull | WRK-099 | - | - |
| WRK-127 | Sanitize and categorize ideal spec.yml templates for OrcaFlex input across structure types | WRK-121 | - | - |
| WRK-137 | Download and parse rig spec PDFs (102 PDFs from 4 operators) | WRK-136 | - | - |
| WRK-193 | UKCS production data module — NSTA/OPRED open data integration (worldenergydata) | WRK-190 | - | - |
| WRK-196 | Canada offshore + emerging basin watch list (C-NLOER NL data; Guyana/Suriname/Namibia/Falklands monitor) | WRK-190 | - | - |

