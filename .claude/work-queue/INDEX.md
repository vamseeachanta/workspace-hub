<!-- AUTO-GENERATED — do not edit by hand -->
<!-- Generated: 2026-02-25T04:14:28Z by generate-index.py -->

# Work Queue Index

> Auto-generated on 2026-02-25T04:14:28Z. Do not edit manually — run `python .claude/work-queue/scripts/generate-index.py` to regenerate.

## Summary

**Total items:** 538

### By Status

| Status | Count |
|--------|-------|
| pending | 115 |
| working | 9 |
| blocked | 5 |
| done | 174 |
| archived | 223 |

### By Priority

| Priority | Count |
|----------|-------|
| high | 263 |
| medium | 223 |
| low | 51 |

### By Complexity

| Complexity | Count |
|------------|-------|
| simple | 84 |
| medium | 233 |
| complex | 97 |

### By Repository

| Repository | Count |
|------------|-------|
| OGManufacturing | 9 |
| aceengineer-admin | 5 |
| aceengineer-strategy | 2 |
| aceengineer-website | 23 |
| achantas-data | 13 |
| acma-projects | 8 |
| assethold | 12 |
| assetutilities | 58 |
| digitalmodel | 185 |
| doris | 25 |
| frontierdeepwater | 4 |
| hobbies | 1 |
| investments | 1 |
| pdf-large-reader | 1 |
| rock-oil-field | 2 |
| sabithaandkrishnaestates | 1 |
| saipem | 5 |
| workspace-hub | 128 |
| worldenergydata | 97 |

### Plan Tracking

| Metric | Count |
|--------|-------|
| Ensemble planning complete | 0 |
| Plans exist | 162 / 538 |
| Plans cross-reviewed | 92 |
| Plans approved | 115 |
| Brochure pending | 11 |
| Brochure updated/synced | 8 |

## Metrics

### Throughput

| Metric | Value |
|--------|-------|
| Total captured | 538 |
| Total archived | 223 |
| Completion rate | 223/538 (41%) |
| Monthly rate (current month) | 67 archived |
| Monthly rate (prior month) | 3 archived |

### Plan Coverage

| Metric | Count | Percentage |
|--------|-------|------------|
| Pending items with plans | 23 / 115 | 20% |
| Plans cross-reviewed | 7 | 21% |
| Plans user-approved | 7 | 21% |

### Aging

| Bucket | Count | Items |
|--------|-------|-------|
| Pending > 30 days | 0 | - |
| Pending > 14 days | 11 | WRK-005, WRK-008, WRK-032, WRK-036, WRK-039, WRK-043, WRK-045, WRK-046, WRK-048, WRK-050, WRK-075 |
| Working > 7 days | 7 | WRK-020, WRK-021, WRK-118, WRK-121, WRK-125, WRK-131, WRK-149 |
| Blocked > 7 days | 5 | WRK-006, WRK-064, WRK-069, WRK-130, WRK-133 |

### Priority Distribution (active items only)

| Priority | Pending | Working | Blocked |
|----------|---------|---------|---------|
| High     | 72 | 5 | 3 |
| Medium   | 36  | 3  | 1  |
| Low      | 7  | 1  | 1  |

## Master Table

| ID | Title | Status | Priority | Complexity | Computer | Provider | Repos | Module | Ensemble? | Plan? | Reviewed? | Approved? | % Done | Brochure | Blocked By |
|-----|-------|--------|----------|------------|----------|----------|-------|--------|-----------|-------|-----------|-----------|--------|----------|------------|
| WRK-001 | Repair sink faucet in powder room at 11511 Piping Rock | archived | medium | simple | - | - | achantas-data | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-002 | Stove repair with factory service at 11511 Piping Rock | archived | medium | simple | - | - | achantas-data | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-003 | Garage clean up | archived | medium | simple | - | - | achantas-data | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-004 | Reorganize storage in upstairs bathroom at 11511 Piping Rock | archived | medium | simple | - | - | achantas-data | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-005 | Clean up email using AI (when safe) | pending | low | medium | ace-linux-1 | claude | achantas-data | - | ❌ | ✅ | ❌ | ❌ | - | - | - |
| WRK-006 | Upload videos from iPhone to YouTube | blocked | low | simple | ace-linux-1 | claude | achantas-data | - | ❌ | ✅ | ❌ | ❌ | - | - | - |
| WRK-007 | Upload videos from Doris computer to YouTube | archived | medium | simple | - | - | achantas-data | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-008 | Upload photos from multiple devices to achantas-media | pending | low | medium | ace-linux-1 | claude | achantas-data | - | ❌ | ✅ | ❌ | ❌ | - | - | - |
| WRK-009 | Reproduce rev30 lower tertiary BSEE field results for repeatability | archived | high | medium | - | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-010 | Rerun lower tertiary analysis with latest BSEE data and validate | archived | high | medium | - | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | WRK-009 |
| WRK-011 | Run BSEE analysis for all leases with field nicknames and geological era grouping | archived | high | complex | - | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | WRK-010 |
| WRK-012 | Audit HSE public data coverage and identify gaps | archived | high | medium | - | - | worldenergydata | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-013 | HSE data analysis to identify typical mishaps by activity and subactivity | archived | high | complex | - | - | worldenergydata | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | WRK-012 |
| WRK-014 | HSE risk index — client-facing risk insights with risk scoring | archived | medium | complex | - | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | WRK-013 |
| WRK-015 | Metocean data extrapolation to target locations using GIS and nearest-source modeling | archived | medium | complex | - | claude | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-016 | BSEE completion and intervention activity analysis for insights | archived | medium | complex | - | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-017 | Streamline BSEE field data analysis pipeline — wellbore, casing, drilling, completions, interventions | archived | high | complex | - | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-018 | Extend BSEE field data pipeline to other regulatory sources (RRC, Norway, Mexico, Brazil) | archived | low | complex | - | claude+gemini | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-019 | Establish drilling, completion, and intervention cost data by region and environment | done | low | complex | ace-linux-1 | claude+gemini | worldenergydata | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | - | - |
| WRK-020 | GIS skill for cross-application geospatial tools — Blender, QGIS, well plotting | working | medium | complex | ace-linux-2 | claude | digitalmodel | - | ❌ | ✅ | ✅ | ✅ | ██░ 95% | - | - |
| WRK-021 | Stock analysis for drastic trend changes, technical indicators, and insider trading benchmarks | working | medium | complex | ace-linux-1 | gemini | assethold | - | ❌ | ✅ | ✅ | ✅ | ██░ 90% | - | - |
| WRK-022 | US property valuation analysis using GIS — location, traffic, and spatial factors | done | medium | complex | ace-linux-1 | gemini | assethold | - | ❌ | ✅ | ❌ | ✅ | ███ 100% | - | - |
| WRK-023 | Property GIS development timeline with future projection and Google Earth animation | in_progress | low | complex | ace-linux-1 | claude | assethold | - | ❌ | ✅ | ❌ | ❌ | ██░ 85% | - | - |
| WRK-024 | Buckskin field BSEE data analysis — Keathley Canyon blocks 785, 828, 829, 830, 871, 872 | archived | high | medium | - | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-025 | AQWA diffraction analysis runner | archived | high | complex | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | ✅ synced | - |
| WRK-026 | Unified input data format converter for diffraction solvers (AQWA, OrcaWave, BEMRosetta) | archived | high | complex | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-027 | AQWA batch analysis execution | archived | high | medium | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | ✅ synced | WRK-025 |
| WRK-028 | AQWA postprocessing - RAOs and verification | archived | high | complex | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | ✅ synced | WRK-025 |
| WRK-029 | OrcaWave diffraction analysis runner + file preparation | archived | high | complex | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-030 | OrcaWave batch analysis + postprocessing | archived | high | complex | - | - | digitalmodel | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | ✅ synced | WRK-029 |
| WRK-031 | Benchmark OrcaWave vs AQWA for 2-3 hulls | archived | medium | complex | - | claude | digitalmodel | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-032 | Modular OrcaFlex pipeline installation input with parametric campaign support | pending | medium | complex | acma-ansys05 | codex | digitalmodel | - | ❌ | ✅ | ❌ | ❌ | - | - | - |
| WRK-033 | Develop OrcaFlex include-file modular skill for parametrised analysis input | archived | medium | complex | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-034 | Develop OrcaWave modular file prep skill for parametrised analysis input | archived | medium | complex | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-035 | Develop AQWA modular file prep skill for parametrised analysis input | archived | medium | complex | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-036 | OrcaFlex structure deployment analysis - supply boat side deployment with structural loads | pending | low | complex | acma-ansys05 | claude | acma-projects | - | ❌ | ✅ | ❌ | ❌ | - | - | - |
| WRK-037 | Get OrcaFlex framework of agreement and terms | archived | medium | simple | - | - | aceengineer-admin | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-038 | Compile global LNG terminal project dataset with comprehensive parameters | archived | medium | complex | - | gemini | worldenergydata | - | ❌ | ✅ | ❌ | ✅ | ███ 100% | - | - |
| WRK-039 | SPM project benchmarking - AQWA vs OrcaFlex | pending | medium | complex | acma-ansys05 | claude | digitalmodel | - | ❌ | ✅ | ❌ | ❌ | - | - | - |
| WRK-040 | Mooring benchmarking - AQWA vs OrcaFlex | archived | medium | complex | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-041 | Develop long-term plan for Hobbies repo | done | low | medium | ace-linux-1 | gemini | hobbies | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | - | - |
| WRK-042 | Develop long-term plan for Investments repo | done | low | medium | ace-linux-1 | gemini | investments | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | - | - |
| WRK-043 | Parametric hull form analysis with RAO generation and client-facing lookup graphs | pending | low | complex | ace-linux-1 | claude | digitalmodel | - | ❌ | ✅ | ❌ | ❌ | █░░ 70% | - | - |
| WRK-044 | Pipeline wall thickness calculations with parametric utilisation analysis | archived | medium | complex | - | - | digitalmodel | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-045 | OrcaFlex rigid jumper analysis - stress and VIV for various configurations | pending | medium | complex | acma-ansys05 | claude | digitalmodel | - | ❌ | ✅ | ❌ | ❌ | - | - | - |
| WRK-046 | OrcaFlex drilling and completion riser parametric analysis | pending | medium | complex | acma-ansys05 | claude | digitalmodel | - | ❌ | ✅ | ❌ | ❌ | - | - | - |
| WRK-047 | OpenFOAM CFD analysis capability for digitalmodel | in_progress | low | complex | ace-linux-2 | claude | digitalmodel | - | ❌ | ✅ | ✅ | ✅ | ██░ 85% | - | - |
| WRK-048 | Blender working configurations for digitalmodel | pending | low | medium | ace-linux-2 | codex | digitalmodel | - | ❌ | ✅ | ❌ | ❌ | - | - | - |
| WRK-049 | Determine dynacard module way forward | archived | medium | medium | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-050 | Hardware consolidation — inventory, assess, repurpose devices + dev environment readiness | pending | medium | complex | ace-linux-1 | claude | workspace-hub | - | ❌ | ✅ | ❌ | ❌ | ██░ 85% | - | - |
| WRK-051 | digitalmodel test coverage improvement | archived | high | complex | - | - | digitalmodel | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-052 | assetutilities test coverage improvement | archived | high | complex | - | - | assetutilities | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-053 | assethold test coverage improvement | archived | medium | medium | - | - | assethold | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-054 | worldenergydata test coverage improvement | archived | medium | medium | - | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-055 | aceengineer-website test coverage improvement | archived | low | simple | - | - | aceengineer-website | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-056 | aceengineer-admin test coverage improvement | archived | medium | medium | - | - | aceengineer-admin | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-057 | Define canonical spec.yml schema for diffraction analysis | archived | high | medium | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-058 | AQWA input backend — spec.yml to single .dat and modular deck files | archived | high | complex | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | WRK-057 |
| WRK-059 | OrcaWave input backend — spec.yml to single .yml and modular includes | archived | high | complex | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | WRK-057 |
| WRK-060 | Common mesh format and converter pipeline (BEMRosetta + GMSH) | archived | high | medium | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-061 | CLI and integration layer for spec converter | archived | medium | medium | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | WRK-058, WRK-059, WRK-060 |
| WRK-062 | Test suite for spec converter using existing example data | archived | high | medium | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | WRK-057 |
| WRK-063 | Reverse parsers — AQWA .dat and OrcaWave .yml to canonical spec.yml | archived | high | complex | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | WRK-057 |
| WRK-064 | OrcaFlex format converter: license-required validation and backward-compat wrapper | blocked | medium | medium | acma-ansys05 | codex | digitalmodel | - | ❌ | ✅ | ❌ | ❌ | - | - | - |
| WRK-065 | S-lay pipeline installation schema + builders for PRPP Eclipse vessel | archived | high | complex | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-066 | Review and improve digitalmodel module structure for discoverability | archived | high | complex | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-067 | Acquire OSHA enforcement and fatality data | archived | high | simple | - | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-068 | Acquire BSEE incident investigations and INCs data | archived | high | medium | - | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-069 | Acquire USCG MISLE bulk dataset | blocked | high | simple | ace-linux-1 | claude | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | - | - | - |
| WRK-070 | Import PHMSA pipeline data and build pipeline_safety module | archived | high | medium | - | - | worldenergydata | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-071 | Acquire NTSB CAROL marine investigations and EPA TRI data | archived | high | simple | - | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-072 | Technical safety analysis module for worldenergydata using ENIGMA theory | archived | high | complex | - | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-073 | Market digitalmodel and worldenergydata capabilities on aceengineer website | archived | high | complex | - | - | aceengineer-website | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-074 | Complete marine safety database importers (MAIB, IMO, EMSA, TSB) | archived | high | complex | - | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-075 | OFFPIPE Integration Module — pipelay cross-validation against OrcaFlex | pending | low | complex | acma-ansys05 | claude | digitalmodel | - | ❌ | ✅ | ❌ | ❌ | - | - | - |
| WRK-076 | Add data collection scheduler/orchestrator for automated refresh pipelines | archived | medium | complex | - | codex | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-077 | Validate and wire decline curve modeling into BSEE production workflow | archived | high | medium | - | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-078 | Create energy data case study — BSEE field economics with NPV/IRR workflow | archived | medium | medium | - | - | aceengineer-website | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-079 | Create marine safety case study — cross-database incident correlation | archived | medium | medium | - | - | aceengineer-website | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | WRK-074 |
| WRK-080 | Write 4 energy data blog posts for SEO | done | low | complex | ace-linux-1 | gemini | aceengineer-website | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-081 | Build interactive NPV calculator for website lead generation | done | low | complex | ace-linux-1 | codex | aceengineer-website | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-082 | Complete LNG terminal data pipeline — from config to working collection | archived | medium | medium | - | - | worldenergydata | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-083 | Validate multi-format export (Excel, PDF, Parquet) with real BSEE data | archived | medium | medium | - | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-084 | Integrate metocean data sources into unified aggregation interface | archived | medium | complex | - | claude | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-085 | Create public sample data access page on website | done | low | medium | ace-linux-1 | codex | aceengineer-website | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | WRK-075 |
| WRK-086 | Rewrite CI workflows for Python/bash workspace | archived | medium | medium | - | - | workspace-hub | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-087 | Improve test coverage across workspace repos | archived | high | complex | - | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-088 | Investigate and clean submodule issues (pdf-large-reader, worldenergydata, aceengineercode) | archived | low | simple | - | - | workspace-hub | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-089 | Review Claude Code version gap and update cc-insights | archived | low | simple | - | - | workspace-hub | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-090 | Identify and refactor large files exceeding 400-line limit | archived | medium | medium | - | - | workspace-hub | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-091 | Add dynacard module README | archived | low | low | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-092 | Register dynacard CLI entry point | archived | low | low | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-093 | Improve dynacard AI diagnostics | archived | low | complex | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | ✅ synced | - |
| WRK-094 | Plan, reassess, and improve the workspace-hub workflow | archived | high | complex | - | - | workspace-hub | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-096 | Review and improve worldenergydata module structure for discoverability | archived | high | medium | - | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-097 | Implement three-tier data residence strategy (worldenergydata ↔ digitalmodel) | archived | high | medium | - | - | workspace-hub, worldenergydata, digitalmodel | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-098 | Clean up 7.1GB large data committed to worldenergydata git history | archived | high | high | - | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-099 | Run 3-way benchmark on Unit Box hull | in_progress | medium | medium | ace-linux-1 | claude | digitalmodel | - | ❌ | ✅ | ✅ | ✅ | ██░ 90% | - | - |
| WRK-100 | Run 3-way benchmark on Barge hull | archived | medium | medium | - | - | digitalmodel | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | WRK-099 |
| WRK-101 | Add mesh decimation/coarsening to mesh-utilities skill | done | low | medium | ace-linux-1 | codex | digitalmodel | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-102 | Add generic hull definition/data for all rigs in worldenergydata | archived | medium | medium | - | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-103 | Add heavy construction/installation vessel data to worldenergydata | archived | medium | medium | - | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-104 | Expand drilling rig fleet dataset to all offshore and onshore rigs | archived | high | complex | - | - | worldenergydata | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | - | - |
| WRK-105 | Add drilling riser component data to worldenergydata | archived | medium | medium | - | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-106 | Hull panel geometry generator from waterline, section, and profile line definitions | done | medium | complex | ace-linux-1 | claude | digitalmodel | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-107 | Clarify Family Dollar 1099-MISC rent amount discrepancy ($50,085.60) | archived | high | simple | - | - | sabithaandkrishnaestates | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-108 | Agent usage credits display — show remaining quota at session start for weekly planning | archived | medium | medium | - | - | workspace-hub | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-109 | Review, refine, and curate hooks + skills — research best practices from existing workflows | archived | medium | medium | - | - | workspace-hub, worldenergydata, digitalmodel | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-110 | Expand hull size library with FST, LNGC, and OrcaFlex benchmark shapes | archived | medium | complex | - | - | digitalmodel | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | - | - |
| WRK-111 | BSEE field development interactive map and analytics | archived | medium | complex | - | claude | worldenergydata, aceengineer-website | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-112 | Appliance lifecycle analytics module for assethold | done | medium | complex | ace-linux-1 | gemini | assethold | - | ❌ | ❌ | ❌ | ❌ | ██░ 90% | - | - |
| WRK-113 | Maintain always-current data index with freshness tracking and source metadata | archived | high | medium | - | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-114 | Collect hull panel shapes and sizes for various floating bodies from existing sources | archived | medium | complex | - | - | digitalmodel, worldenergydata | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | - | - |
| WRK-115 | Link RAO data to hull shapes in hull library catalog | archived | medium | medium | - | - | digitalmodel | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | - | - |
| WRK-116 | Scale hull panel meshes to target principal dimensions for hydrodynamic analysis | archived | medium | medium | - | - | digitalmodel | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | - | - |
| WRK-117 | Refine and coarsen hull panel meshes for mesh convergence sensitivity analysis | archived | medium | complex | - | - | digitalmodel | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | - | - |
| WRK-118 | AI agent utilization strategy — leverage Claude, Codex, Gemini for planning, development, testing workflows | working | medium | complex | ace-linux-1 | claude | workspace-hub | - | ❌ | ✅ | ❌ | ✅ | ░░░ 40% | n/a | - |
| WRK-119 | Test suite optimization — tiered test profiles for commit, task, and session workflows | archived | high | complex | - | - | workspace-hub, worldenergydata, digitalmodel | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-120 | Research and purchase a smart watch | archived | low | simple | - | - | achantas-data | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-121 | Extract & Catalog OrcaFlex Models from rock-oil-field/s7 | working | high | medium | orcaflex-license-machine | claude | workspace-hub | - | ❌ | ✅ | ❌ | ❌ | - | - | - |
| WRK-122 | Licensed Software Usage Workflow & Burden Reduction | archived | high | medium | - | - | acma-projects, assetutilities | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | - | - |
| WRK-124 | Session 20260211_095832 — 1 file(s) created | archived | medium | low | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-125 | OrcaFlex module roadmap — evolving coordination and progress tracking | working | high | low | acma-ansys05 | claude | digitalmodel | - | ❌ | ✅ | ❌ | ❌ | - 10% | - | - |
| WRK-126 | Benchmark all example models across time domain and frequency domain with seed equivalence | pending | high | complex | ace-linux-1 | claude | digitalmodel | - | ❌ | ✅ | ✅ | ✅ | ██░ 75% | - | - |
| WRK-127 | Sanitize and categorize ideal spec.yml templates for OrcaFlex input across structure types | archived | high | medium | - | - | digitalmodel | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | - | WRK-121 |
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | done | high | complex | - | codex | digitalmodel | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | - | - |
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | archived | high | complex | - | codex | digitalmodel | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | - | - |
| WRK-130 | Standardize analysis reporting for each OrcaWave structure type | blocked | high | complex | acma-ansys05 | codex | digitalmodel | - | ❌ | ✅ | ✅ | ❌ | - | - | - |
| WRK-131 | Passing ship analysis for moored vessels — AQWA-based force calculation and mooring response | working | high | complex | orcaflex-license-machine | claude | digitalmodel | - | ❌ | ✅ | ✅ | ✅ | █░░ 60% | - | - |
| WRK-132 | Refine OrcaWave benchmarks: barge/ship/spar RAO fixes + damping/gyradii/Km comparison | archived | high | medium | - | codex+claude | digitalmodel | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | - | - |
| WRK-133 | Update OrcaFlex license agreement with addresses and 3rd-party terms | blocked | high | medium | acma-ansys05 | claude | aceengineer-admin | - | ❌ | ❌ | ✅ | ❌ | - | n/a | - |
| WRK-134 | Add future-work brainstorming step before archiving completed items | archived | medium | medium | - | - | workspace-hub | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-135 | Ingest XLS historical rig fleet data (163 deepwater rigs) | archived | medium | medium | - | - | worldenergydata | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-137 | Download and parse rig spec PDFs (102 PDFs from 4 operators) | parked | low | complex | ace-linux-1 | gemini | worldenergydata | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-138 | Fitness-for-service module enhancement: wall thickness grid, industry targeting, and asset lifecycle | archived | medium | complex | - | - | digitalmodel | asset_integrity | ❌ | ✅ | ✅ | ✅ | ░░░ 40% | ✅ updated | - |
| WRK-139 | Develop gmsh skill and documentation | archived | medium | medium | - | - | workspace-hub | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | - | - |
| WRK-139 | Unified multi-agent orchestration architecture (Claude/Codex/Gemini) | archived | high | complex | - | - | workspace-hub | agents | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-140 | Integrate gmsh meshing skill into digitalmodel and solver pipelines | pending | medium | medium | ace-linux-2 | codex | digitalmodel, workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ██░ 85% | - | - |
| WRK-141 | Create Achantas family tree to connect all family members | done | medium | medium | ace-linux-1 | claude | achantas-data | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-142 | Review work accomplishments and draft Anthropic outreach message | archived | high | medium | - | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-143 | Full symmetric M-T envelope — closed polygon lens shapes | archived | medium | simple | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-144 | API RP 2RD + API STD 2RD riser wall thickness — WSD & LRFD combined loading | archived | medium | complex | - | - | digitalmodel | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-145 | Design code versioning — handle changing revisions of standards | archived | medium | medium | - | - | digitalmodel | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-146 | Overhaul aceengineer-website: fix positioning, narrative, and social proof | done | high | complex | ace-linux-1 | claude+gemini | aceengineer-website | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-147 | Set up aceengineer-strategy private repo with business operations framework | done | high | complex | ace-linux-1 | claude | aceengineer-strategy | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-148 | ACE-GTM: A&CE Go-to-Market strategy stream | pending | high | complex | ace-linux-1 | claude | aceengineer-website, aceengineer-strategy, workspace-hub | - | ❌ | ✅ | ✅ | ✅ | ░░░ 35% | n/a | - |
| WRK-149 | digitalmodel test coverage improvement (re-creates WRK-051) | working | high | complex | ace-linux-1 | codex+claude,gemini | digitalmodel | - | ❌ | ✅ | ✅ | ✅ | █░░ 70% | n/a | - |
| WRK-150 | assetutilities test coverage improvement (re-creates WRK-052) | done | medium | medium | ace-linux-1 | codex | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-151 | worldenergydata test coverage improvement (re-creates WRK-054) | archived | medium | medium | - | codex | worldenergydata | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-152 | Marine safety importer validation — verify MAIB/TSB/IMO/EMSA importers against real data | archived | high | medium | - | codex | worldenergydata | marine_safety | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-153 | Energy data case study — BSEE field economics with NPV/IRR workflow | archived | medium | medium | - | claude | aceengineer-website | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-154 | CI workflow rewrite — fix 2 GitHub Actions workflows | archived | high | medium | - | codex | workspace-hub | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-155 | DNV-ST-F101 submarine pipeline wall thickness — WSD and LRFD methods | archived | high | complex | - | claude | digitalmodel | structural | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-156 | FFS Phase 1 — wall thickness grid input with Level 1/2 accept-reject workflow | done | high | complex | ace-linux-1 | claude | digitalmodel | asset_integrity | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-157 | Fatigue analysis module enhancement — S-N curve reporting and parametric sweeps | archived | high | complex | - | claude | digitalmodel | fatigue | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-158 | Wall thickness parametric engine — Cartesian sweep across D/t, pressure, material | archived | medium | medium | - | claude | digitalmodel | structural | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-159 | Three-way design code comparison report — API RP 1111 vs RP 2RD vs STD 2RD | archived | medium | medium | - | claude | digitalmodel | structural | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-160 | OSHA severe injury + fatality data completion and severity mapping fix | archived | medium | simple | - | claude | worldenergydata | hse | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-161 | BSEE Excel statistics re-download and URL importer verification | archived | medium | simple | - | claude | worldenergydata | hse | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-163 | Well planning risk empowerment framework | archived | medium | complex | - | claude | worldenergydata, digitalmodel | risk_assessment | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-164 | Well production test data quality and nodal analysis foundation | archived | high | complex | - | claude | worldenergydata, digitalmodel | production_engineering | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-165 | Research subsea intervention analysis opportunities | done | medium | medium | ace-linux-1 | gemini | digitalmodel, worldenergydata | subsea_intervention | ❌ | ✅ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-166 | Jabra USB dongle lost — research universal dongle compatibility | done | medium | simple | ace-linux-1 | gemini | - | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-167 | Calendar: Krishna ADHD evaluation — 24 Feb 2:30 PM | done | high | simple | ace-linux-1 | claude | - | - | ❌ | ✅ | ❌ | ✅ | ███ 100% | n/a | - |
| WRK-167 | Calendar: Krishna ADHD evaluation — 24 Feb 2:30 PM | archived | high | simple | ace-linux-1 | claude | - | - | ❌ | ✅ | ❌ | ✅ | ███ 100% | n/a | - |
| WRK-168 | MPD systems knowledge module — pressure management for drillships | archived | high | complex | - | claude | worldenergydata, digitalmodel | drilling_pressure_management | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-169 | Drilling technology evolution — MPD adoption case study | done | medium | medium | ace-linux-1 | gemini | aceengineer-website, worldenergydata | content | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-170 | Integrate MET-OM/metocean-stats as statistical analysis engine for metocean module | archived | medium | complex | - | claude | worldenergydata, digitalmodel | metocean | ❌ | ✅ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-171 | Cost data calibration — sanctioned project benchmarking & multivariate cost prediction | pending | medium | complex | ace-linux-1 | claude | worldenergydata | cost | ❌ | ✅ | ❌ | ❌ | ██░ 80% | n/a | - |
| WRK-172 | AI agent usage tracking — real-time quota display, OAuth API, session hooks | archived | high | medium | - | claude | workspace-hub | ai-tools | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-173 | Session Management Workflow Documentation + Schematic | done | high | low | ace-linux-1 | claude | workspace-hub | - | ❌ | ✅ | ❌ | ❌ | - | - | - |
| WRK-175 | Session Start: Engineering Context Loader | done | medium | medium | ace-linux-1 | claude+gemini | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-176 | Session Start: Design Code Version Guard | done | high | low | ace-linux-1 | codex | workspace-hub, digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-177 | Stop Hook: Engineering Calculation Audit Trail | archived | high | medium | - | claude+codex | workspace-hub, worldenergydata | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | - | - |
| WRK-178 | Stop Hook: Data Provenance Snapshot | archived | medium | medium | - | codex | workspace-hub, worldenergydata | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | - | - |
| WRK-179 | Start Hook: Agent Capacity Pre-flight | archived | medium | low | - | codex | workspace-hub | - | ❌ | ❌ | ❌ | ✅ | ███ 100% | - | - |
| WRK-180 | Stop Hook: Cross-Agent Learning Sync | parked | low | high | ace-linux-1 | claude+gemini | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | - | - | - |
| WRK-181 | Session Replay & Time Travel | parked | low | high | ace-linux-1 | claude | workspace-hub | - | ❌ | ✅ | ❌ | ❌ | - 10% | - | - |
| WRK-182 | Predictive Session Planning | parked | low | high | ace-linux-1 | claude+gemini | workspace-hub | - | ❌ | ✅ | ❌ | ❌ | █░░ 60% | - | - |
| WRK-183 | Domain Knowledge Graph | done | medium | high | ace-linux-1 | claude+gemini | workspace-hub, worldenergydata, digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-184 | Improve /improve — Bug fixes, recommendations output, startup readiness | archived | high | medium | - | claude | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-185 | Ecosystem Truth Review: instruction/skills/work-item centralization | archived | high | medium | - | codex+claude | workspace-hub, digitalmodel, worldenergydata | governance | ❌ | ✅ | ✅ | ❌ | ███ 100% | n/a | - |
| WRK-186 | Context budget: trim rules/ to under 16KB | archived | high | simple | - | claude | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-187 | Improve /improve: usage-based skill health, classify retry, apply API content | archived | medium | medium | - | claude | workspace-hub | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | - | - |
| WRK-188 | Wave-1 spec migration: worldenergydata dry-run manifest and apply plan | archived | high | medium | - | codex+claude | workspace-hub, worldenergydata | governance | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-190 | NCS production data module — NPD/Sodir open data integration (worldenergydata) | archived | medium | moderate | - | codex | worldenergydata | ncs | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-191 | Field development case study catalog — structured reference library of real projects | done | medium | moderate | ace-linux-1 | gemini | digitalmodel | field_development_references | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-192 | Field development schematic generator — Python SVG/PNG layout diagrams | done | medium | complex | ace-linux-1 | codex | digitalmodel | field_development_visuals | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-193 | UKCS production data module — NSTA/OPRED open data integration (worldenergydata) | archived | low | moderate | - | codex | worldenergydata | ukcs | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-194 | Brazil ANP production data module — well-level monthly CSV integration (worldenergydata) | archived | high | moderate | - | codex | worldenergydata | brazil_anp | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-195 | EIA US production data module — non-GoM onshore + Alaska integration (worldenergydata) | archived | medium | moderate | - | codex | worldenergydata | eia_us | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-196 | Canada offshore + emerging basin watch list (C-NLOER NL data; Guyana/Suriname/Namibia/Falklands monitor) | archived | low | moderate | - | codex | worldenergydata, digitalmodel | canada_offshore + emerging_basins | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | WRK-190 |
| WRK-197 | Nigeria NUPRC + EITI data framework — West Africa deepwater and multi-country payment data | done | low | moderate | ace-linux-1 | codex | worldenergydata | west_africa | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-198 | HSE risk index interactive web dashboard | done | medium | complex | ace-linux-1 | claude | aceengineer-website | demos/hse-risk-dashboard.html | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-199 | AI agent usage optimizer skill — maximize Claude/Codex/Gemini allocation per task | done | medium | medium | ace-linux-1 | claude | workspace-hub | ai-tools | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-200 | Filesystem naming cleanup — eliminate duplicate/conflicting dirs across workspace-hub, digitalmodel, worldenergydata | archived | high | complex | - | claude | - | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | - | - |
| WRK-201 | Work queue workflow gate enforcement — plan_reviewed, Route C spec, pre-move checks | archived | high | medium | - | claude | workspace-hub | work-queue | ❌ | ❌ | ❌ | ❌ | ███ 100% | ⏳ pending | - |
| WRK-204 | digitalmodel: rename modules/ naming pattern across docs/, examples/, scripts/python/, base_configs/, tests/ | archived | medium | complex | - | claude | - | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | - | - |
| WRK-205 | Skills knowledge graph — capability metadata and relationship layer beyond flat index | archived | medium | medium | - | - | workspace-hub | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-206 | Asset integrity / fitness-for-service (FFS) engineering skill — corrosion damage assessment and run-repair-replace decisions | archived | medium | medium | - | - | workspace-hub, digitalmodel | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-207 | Skill relationship maintenance — bidirectional linking as enforced process | archived | medium | small | - | claude | workspace-hub | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | - | - |
| WRK-207 | Wire model-tier routing into work queue plan.sh and execute.sh — Sonnet 4.6 default, Opus 4.6 for Route C plan only | archived | medium | simple | - | - | workspace-hub | - | ❌ | ✅ | ❌ | ✅ | ███ 100% | n/a | - |
| WRK-208 | Cross-platform encoding guard — pre-commit + post-pull encoding validation | archived | high | simple | - | claude | workspace-hub | - | ❌ | ❌ | ❌ | ✅ | ███ 100% | n/a | - |
| WRK-209 | Add unit validator to EnvironmentSpec.water_density — catch physically implausible values | done | medium | small | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | - | - |
| WRK-209 | uv enforcement across workspace — eliminate python3/python fallback chains | archived | medium | medium | - | claude | workspace-hub | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-210 | Interoperability skill — cross-OS standards and health checks for workspace-hub | archived | medium | small | - | claude | workspace-hub | - | ❌ | ✅ | ❌ | ✅ | ███ 100% | n/a | - |
| WRK-211 | Ecosystem health check skill — parallel agent for session and repo-sync workflows | archived | medium | medium | - | claude | workspace-hub | - | ❌ | ❌ | ❌ | ✅ | ███ 100% | n/a | - |
| WRK-212 | Agent teams protocol skill — orchestrator routing, subagent patterns, team lifecycle | archived | medium | medium | - | claude | workspace-hub | - | ❌ | ❌ | ❌ | ✅ | ███ 100% | n/a | - |
| WRK-213 | Codex multi-agent roles — assess native role system vs workspace-hub agent skill approach | archived | medium | medium | - | claude | workspace-hub | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-214 | Session lifecycle compliance — interview-driven review of all workflow scaffolding | archived | high | medium | - | claude | workspace-hub | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-215 | Graph-aware skill discovery and enhancement — extend /improve with proactive gap analysis | archived | medium | simple | - | claude | workspace-hub | - | ❌ | ✅ | ❌ | ✅ | ███ 100% | n/a | WRK-205 |
| WRK-216 | Subagent learning capture — emit signals to pending-reviews before task completion | archived | medium | simple | - | claude | workspace-hub | - | ❌ | ✅ | ❌ | ✅ | ███ 100% | n/a | - |
| WRK-217 | Update ecosystem-health-check.sh — remove stale skill count threshold | archived | medium | simple | - | claude | workspace-hub | - | ❌ | ✅ | ❌ | ✅ | ███ 100% | n/a | - |
| WRK-218 | Well bore design analysis — slim-hole vs. standard-hole hydraulic and mechanical trade-offs | archived | medium | complex | - | claude+gemini | digitalmodel, worldenergydata | well_design | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-219 | Batch drilling economics analysis — campaign scheduling and cost optimization | pending | medium | medium | ace-linux-1 | gemini+claude | worldenergydata, digitalmodel | drilling_economics | ❌ | ❌ | ❌ | ❌ | ██░ 90% | n/a | - |
| WRK-220 | Offshore decommissioning analytics — data-driven lifecycle planning module | archived | medium | complex | - | claude+gemini | worldenergydata, digitalmodel, aceengineer-website | decommissioning_analytics | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-221 | Offshore resilience design framework — modular platforms, lifecycle planning, structural monitoring | done | low | medium | ace-linux-1 | gemini+claude | digitalmodel, aceengineer-website | offshore_resilience | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-222 | Pre-clear session snapshot — /save skill + save-snapshot.sh script | archived | medium | low | - | - | workspace-hub | - | ❌ | ❌ | ❌ | ✅ | ███ 100% | - | - |
| WRK-223 | Workstations registry — hardware inventory, hardware-info.sh, ace-linux-1 specs | archived | medium | low | - | claude | workspace-hub | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | - | - |
| WRK-224 | Tool-readiness SKILL.md — session-start check for CLI, data sources, statusline, work queue | done | medium | low | ace-linux-1 | claude | workspace-hub | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | - | - |
| WRK-224 | Tool-readiness SKILL.md — session-start check for CLI, data sources, statusline, work queue | archived | medium | low | - | claude | workspace-hub | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | - | - |
| WRK-225 | Investigate plugins vs skills trade-off for repo ecosystem | archived | medium | medium | - | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-226 | Audit and improve agent performance files across Claude, Codex, and Gemini | done | high | medium | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-226 | Audit and improve agent performance files across Claude, Codex, and Gemini | archived | high | medium | - | - | workspace-hub | - | ❌ | ✅ | ❌ | ✅ | ███ 100% | n/a | - |
| WRK-227 | Evaluate cowork relevance — repo ecosystem fit vs agentic coding momentum | parked | medium | medium | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-228 | Cross-machine terminal UX consistency — Windows Git Bash vs Linux terminal | done | high | medium | ace-linux-1 | - | - | - | ❌ | ❌ | ❌ | ❌ | ██░ 95% | - | - |
| WRK-228 | Orient all work items toward agentic AI future-boosting, not just task completion | archived | high | medium | - | - | workspace-hub | - | ❌ | ✅ | ❌ | ✅ | ███ 100% | n/a | - |
| WRK-229 | AI agent QA closure — HTML output + SME verification loop per work item | done | high | medium | ace-linux-1 | - | - | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-229 | Skills curation — online research, knowledge graph review, update index, session-input health check | done | high | medium | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ✅ | ███ 100% | n/a | - |
| WRK-229 | Skills curation — online research, knowledge graph review, update index, session-input health check | archived | high | medium | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ✅ | ███ 100% | n/a | - |
| WRK-230 | Holistic session lifecycle — unify gap surfacing, stop hooks, and skill input pipeline | archived | high | medium | - | - | workspace-hub | - | ❌ | ❌ | ❌ | ✅ | ███ 100% | n/a | - |
| WRK-231 | session-analysis skill — first-class session mining as foundation for skills, gaps, and agent improvement | archived | high | medium | - | - | workspace-hub | - | ❌ | ❌ | ❌ | ✅ | ███ 100% | n/a | - |
| WRK-232 | session-bootstrap skill — one-time historical session analysis per machine | archived | high | simple | - | - | workspace-hub | - | ❌ | ❌ | ❌ | ✅ | ███ 100% | n/a | WRK-231 |
| WRK-233 | Assess and simplify existing workflows in light of session-analysis self-learning loop | archived | high | medium | - | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | WRK-231 |
| WRK-234 | MISSION: Self-improving agent ecosystem — sessions drive skills, skills drive better sessions | pending | high | complex | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ██░ 90% | n/a | - |
| WRK-235 | ROADMAP: Repo ecosystem 3-6 month horizon — plan and gear for agentic AI maturation | working | high | complex | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ██░ 80% | n/a | - |
| WRK-236 | Test health trends — track test-writing pairing with code-writing sessions | done | medium | medium | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | WRK-231 |
| WRK-237 | Provider cost tracking — token spend per session and per WRK item | done | medium | medium | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | WRK-231 |
| WRK-238 | Adopt Codex 0.102.0 TOML role definitions — implement native multi-agent roles in .codex/ | done | medium | medium | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-239 | BSEE field pipeline skill — zero-config agent-callable wrapper | archived | high | medium | - | - | worldenergydata | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-240 | Diffraction spec converter skill — register as named agent-callable skill | archived | high | simple | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-241 | Pipeline integrity skill — chain wall thickness, parametric engine, and FFS into one callable workflow | archived | high | medium | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-242 | Multi-format export as automatic pipeline output stage | archived | high | medium | - | - | worldenergydata, digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-243 | Hull analysis setup skill — chain select, scale, mesh, RAO-link into one call | archived | high | medium | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-244 | OrcaFlex template library skill — get canonical spec.yml by structure type | archived | high | simple | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-245 | Fatigue assessment skill — wrap full module with input schema and auto export | archived | high | medium | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-246 | LNG terminal dataset — queryable module and aceengineer website data card | archived | medium | medium | - | - | worldenergydata, aceengineer-website | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-247 | digitalmodel capability manifest — machine-readable module index for agent discovery | archived | medium | simple | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-248 | PHMSA pipeline safety case study — aceengineer website with data-to-assessment workflow | archived | medium | medium | - | - | aceengineer-website, worldenergydata | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-249 | ENIGMA safety analysis skill — register as agent-callable capability | archived | medium | medium | - | - | worldenergydata | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-250 | Cross-database marine safety case study — MAIB, IMO, EMSA, TSB correlation analysis | archived | medium | medium | - | - | worldenergydata, aceengineer-website | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-251 | Dynacard vision model evaluation — benchmark GPT-4V / Claude Vision vs current heuristics | done | medium | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-252 | worldenergydata module discoverability review — regenerate after new data source modules | archived | medium | simple | - | - | worldenergydata | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-253 | Data residence tier compliance audit and extension to assethold | done | medium | medium | ace-linux-1 | - | worldenergydata, digitalmodel, assethold | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-254 | Heavy vessel GIS integration — connect vessel dataset to GIS skill and BSEE pipeline | done | medium | medium | ace-linux-1 | - | worldenergydata, digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-255 | Hull library lookup skill — closest-match hull form by target dimensions | archived | medium | simple | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-256 | Unified parametric study coordinator — orchestrate OrcaFlex, wall thickness, and fatigue sweeps | in-progress | medium | complex | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ✅ | ✅ | ██░ 95% | n/a | - |
| WRK-257 | Agent coordination model ADR — document architectural decision record | done | low | simple | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-258 | Close WRK-153 as superseded — defer BSEE case study rebuild to after WRK-019 and WRK-171 | archived | low | simple | - | - | worldenergydata | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-259 | BSEE field economics case study — calibrated NPV/IRR with cost data foundation | pending | medium | medium | ace-linux-1 | claude | aceengineer-website, worldenergydata | - | ❌ | ❌ | ❌ | ❌ | - | n/a | WRK-019, WRK-171 |
| WRK-259 | common.units — global unit conversion registry for cross-basin analysis | archived | high | medium | - | claude | worldenergydata | common.units | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-260 | Cross-regional production data query interface — unified layer across all 8 basins | archived | high | moderate | - | claude | worldenergydata | production.unified | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-261 | BSEE field economics case study — rebuild on calibrated cost data (WRK-019 + WRK-171) | pending | medium | medium | ace-linux-1 | claude | aceengineer-website | - | ❌ | ❌ | ❌ | ❌ | - | n/a | WRK-019, WRK-171 |
| WRK-262 | Add path-handling guidance to session preflight hook | done | low | simple | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-263 | Progressively reduce agent harness files to ~20 lines by migrating content to skills | done | high | medium | ace-linux-1 | - | workspace-hub | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-264 | Ensure full work-queue workflow parity between Claude and Codex CLI | done | low | medium | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-265 | Wire CrossDatabaseAnalyzer to live MAIB/IMO/EMSA/TSB importers | archived | high | medium | - | claude | worldenergydata | marine_safety | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-266 | Calibrate decommissioning cost model against BSEE platform removal notices | archived | medium | medium | - | claude | worldenergydata | decommissioning | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-267 | Calibrate well planning risk probabilities against BSEE incident and HSE data | archived | medium | medium | - | claude | worldenergydata | well_planning | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-268 | Wire ENIGMA safety skill to real HSE incident database for data-driven scoring | archived | medium | medium | - | claude | worldenergydata | safety_analysis | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-269 | CP standards research — inventory codes, map version gaps, define implementation scope | archived | high | medium | - | gemini+claude | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-270 | Fix cathodic-protection SKILL.md — align examples to real CathodicProtection API | archived | medium | simple | - | claude | workspace-hub | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-271 | CP worked examples — end-to-end reference calculations for pipeline, ship, and offshore platform | archived | medium | medium | - | claude+codex | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | WRK-276, WRK-279 |
| WRK-272 | CP capability extension — DNV-RP-B401 offshore platform + DNV-RP-F103 2016 update | archived | medium | complex | - | claude+codex | digitalmodel | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-273 | CP marketing brochure — cathodic protection capability document for aceengineer-website | done | low | simple | ace-linux-1 | gemini+claude | digitalmodel, aceengineer-website | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | ⏳ pending | - |
| WRK-274 | saipem repo content index — searchable catalog of disciplines, project files, and key docs | archived | medium | simple | - | gemini+claude | saipem | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-275 | acma-projects repo content index — catalog projects, codes & standards, and key reference docs | archived | medium | simple | - | gemini+claude | acma-projects | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-276 | Abstract all CP client calcs to .md reference — strip project names, keep engineering data, use as tests | archived | high | medium | - | claude+gemini | digitalmodel, saipem, acma-projects | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-277 | CP capability — ABS GN Offshore Structures 2018 route for ABS-classed offshore structures | archived | medium | complex | - | claude+codex | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-278 | Wire legal-sanity-scan into pre-commit for CP-stream repos — activate deny list CI gate | archived | high | simple | - | claude+codex | digitalmodel, saipem, acma-projects | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | WRK-276 |
| WRK-279 | Audit & govern the /mnt/ace/ Codex relocation plan | complete | high | medium | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ✅ | ██░ 90% | n/a | - |
| WRK-279 | Fix DNV_RP_F103_2010 critical defects G-1 through G-4 — replace fabricated table refs + non-standard formulas | archived | critical | medium | - | claude+codex | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-280 | ABS standards acquisition: create folder + download CP Guidance Notes | done | high | simple | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ✅ | █░░ 70% | n/a | - |
| WRK-280 | ABS standards acquisition: create folder + download CP Guidance Notes | archived | high | simple | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ✅ | █░░ 70% | n/a | - |
| WRK-281 | Fix 2H legacy project discoverability (navigation layer) | done | medium | simple | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-282 | Migrate raw ABS docs from O&G-Standards/raw/ into structured ABS/ folder | archived | high | simple | - | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-283 | Navigation layer for 0_mrv/, Production/, umbilical/ legacy roots | archived | medium | simple | - | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-285 | Write active WRK id to state file on working/ transition | archived | high | simple | - | - | workspace-hub | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-286 | Harden chore: commits — require WRK ref for multi-file changes | done | medium | simple | ace-linux-1 | - | workspace-hub | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | - | - |
| WRK-287 | Set up Linux-to-Linux network file sharing for workspace-hub access from ace-linux-2 | archived | medium | medium | - | - | workspace-hub | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-288 | Finish ace-linux-2 setup — install open source engineering programs and map capabilities | done | low | simple | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | WRK-289, WRK-290, WRK-291, WRK-292 |
| WRK-289 | Research open source FEA programs for engineering assignments | done | low | medium | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-290 | Install core engineering suite on ace-linux-2 (Blender, OpenFOAM, FreeCAD, Gmsh, BemRosetta) | done | medium | medium | ace-linux-2 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-290 | Install core engineering suite on ace-linux-2 (Blender, OpenFOAM, FreeCAD, Gmsh, BemRosetta) | archived | medium | medium | ace-linux-2 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-291 | Install recommended FEA programs on ace-linux-2 | done | low | medium | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-292 | Create capability map — file formats, workflow pipelines, interoperability matrix | done | low | medium | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | WRK-290, WRK-291 |
| WRK-293 | SMART health check on ace-linux-2 drives — install smartmontools + run diagnostics | done | high | simple | ace-linux-2 | - | workspace-hub | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-294 | Standardize ace-linux-2 mount paths — fstab entries for HDDs with clean paths | in-progress | high | simple | ace-linux-2 | - | workspace-hub | - | ❌ | ❌ | ✅ | ✅ | ██░ 80% | n/a | - |
| WRK-295 | Bidirectional SSH key auth between ace-linux-1 and ace-linux-2 | done | high | simple | ace-linux-2 | - | workspace-hub | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-296 | Install Tailscale VPN on ace-linux-2 — match ace-linux-1 remote access | done | medium | simple | ace-linux-2 | - | workspace-hub | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-297 | SSHFS mounts on ace-linux-1 for ace-linux-2 drives — bidirectional file access | pending | high | simple | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ✅ | ✅ | - | n/a | WRK-294 |
| WRK-298 | Install smartmontools on ace-linux-1 + SMART health check on all drives | done | high | simple | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-299 | comprehensive-learning skill — single batch command for all session learning + ecosystem improvement | archived | high | medium | - | - | - | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-300 | workstations skill — evolve from registry to multi-machine work distribution | archived | medium | medium | - | - | - | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-301 | fix: recurring Write correction pattern — not responding to improve | done | medium | medium | ace-linux-1 | - | - | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-302 | fix: recurring Edit correction pattern — not responding to improve | done | medium | medium | ace-linux-1 | - | - | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-303 | Ensemble planning — 3×Claude + 3×Codex + 3×Gemini independent agents for non-deterministic plan diversity | archived | medium | medium | - | - | workspace-hub | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | ⏳ pending | - |
| WRK-304 | cleanup: one lean Stop hook — consume-signals.sh only, all analysis to nightly cron | done | high | medium | ace-linux-1 | - | - | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-305 | feat: session signal emitters — wire /clear, plan-mode, per-WRK tool-counts | done | medium | medium | ace-linux-1 | - | - | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-306 | feat: AI agent readiness check — claude/codex/gemini CLI versions + default models | done | medium | medium | ace-linux-1 | - | - | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-307 | track: lean-session hook requirement missed — accountability record | done | high | medium | ace-linux-1 | - | - | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-307 | Fix KVM display loss on ace-linux-2 after switching — EDID emulator or config fix | archived | medium | simple | ace-linux-2 | - | workspace-hub | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-308 | perf: move pre-commit skill validation + readiness checks to nightly cron | done | high | medium | any | - | - | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-309 | chore: portable Python invocation — consistent cross-machine execution, zero error noise | archived | high | medium | - | - | workspace-hub | - | ❌ | ✅ | ✅ | ✅ | ██░ 90% | ⏳ pending | - |
| WRK-310 | explore: OrcFxAPI schematic capture for OrcaWave models (program screenshots) | pending | medium | medium | - | - | digitalmodel, workspace-hub | - | ❌ | ❌ | ❌ | ❌ | █░░ 60% | n/a | - |
| WRK-310 | Daily network-mount readiness check — SSHFS mounts always available on both machines | archived | high | low | - | - | workspace-hub | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-311 | improve: QTF benchmarking for case 3.1 — charts, comparisons, and validation depth | pending | high | medium | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-313 | feat: new-machine setup guide + bootstrap script — statusline, CLI parity, cron jobs | done | high | medium | any | - | - | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-314 | OrcaFlex Reporting Phase 4 — OrcFxAPI Integration | done | high | medium | - | - | - | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-315 | CALM buoy mooring fatigue — spectral fatigue from OrcaFlex time-domain output | done | medium | high | acma-ansys05 | - | digitalmodel | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-316 | NDBC buoy data ingestion for metocean wave scatter matrices | done | medium | medium | ace-linux-1 | - | worldenergydata, digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-317 | Integrated web dashboard — Plotly Dash for BSEE and FDAS data | done | medium | high | ace-linux-1 | - | worldenergydata | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-319 | Real-time EIA and IEA feed ingestion — weekly crude and gas production | done | medium | medium | ace-linux-1 | - | worldenergydata | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-320 | MAIB and NTSB incident correlation with USCG MISLE for root-cause taxonomy | done | low | high | ace-linux-1 | - | worldenergydata | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-321 | Field development economics — MIRR NPV with carbon cost sensitivity | done | medium | medium | ace-linux-1 | - | worldenergydata | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-322 | Fundamentals scoring — P/E P/B EV/EBITDA ranking from yfinance | done | high | medium | ace-linux-1 | - | assethold | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-323 | Covered call analyser — option chain ingestion and premium yield calculator | done | medium | medium | ace-linux-1 | - | assethold | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-324 | Risk metrics — VaR CVaR Sharpe ratio max drawdown per position and portfolio | done | high | medium | ace-linux-1 | - | assethold | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-325 | Sector exposure tracker — auto-classify holdings by GICS sector and flag concentration | done | medium | medium | ace-linux-1 | - | assethold | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-326 | Unified CLI — single ace command routing to all repo tools | done | medium | high | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-327 | Shared engineering constants library — material properties unit conversions seawater properties | done | medium | medium | ace-linux-1 | - | workspace-hub, digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-328 | Agent-readable specs index — YAML index of all specs consumable by AI agents | done | medium | medium | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-329 | Formalise doris calculation workflow — migrate ad-hoc calcs to Python modules | done | medium | high | ace-linux-1 | - | doris | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-330 | DNV-ST-F101 pressure containment checks for subsea pipelines | done | medium | medium | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-331 | API RP 1111 deepwater pipeline design checks — collapse and propagating buckle | done | medium | medium | ace-linux-1 | - | doris | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-332 | On-bottom stability module — DNV-RP-F109 soil resistance calculations | done | medium | medium | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-335 | Drilling engineering module — casing design checks per API TR 5C3 | done | medium | high | ace-linux-1 | - | OGManufacturing | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-336 | Portable installation analysis library — extract generic OrcaFlex automation from project code | done | medium | high | acma-ansys05 | - | saipem, rock-oil-field | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-337 | Vessel weather-window calculator — operability analysis from Hs Tp scatter | done | medium | medium | ace-linux-1 | - | saipem, rock-oil-field | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-338 | LNG tank structural checks — API 620 and EN 14620 thin-shell hoop stress | done | medium | medium | ace-linux-1 | - | acma-projects | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-339 | Aluminium structural module — Eurocode 9 and AA ADM member capacity checks | done | medium | medium | ace-linux-1 | - | acma-projects | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-340 | Composite panel design tool — Classical Laminate Theory CLT strength checks | done | medium | high | ace-linux-1 | - | acma-projects | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-341 | Review pdf-large-reader vs native AI agent PDF capabilities — assess continuation or deprecation | done | medium | simple | ace-linux-1 | - | pdf-large-reader, workspace-hub | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-342 | Multi-machine workflow clarity — SSH helper scripts, hostname in statusline, CLI consistency across ace-linux-1 and ace-linux-2 | done | high | medium | ace-linux-2 | - | workspace-hub | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-343 | OpenFOAM technical debt and exploration — tutorials, ecosystem audit, WRK-047 refresh | pending | medium | medium | ace-linux-2 | - | workspace-hub, digitalmodel | - | ❌ | ❌ | ✅ | ❌ | ██░ 85% | n/a | - |
| WRK-344 | Remove agent_os from assetutilities | done | high | simple | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-345 | Consolidate validators package into assetutilities | done | high | simple | ace-linux-1 | - | assetutilities, worldenergydata, assethold | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-346 | Fix aceengineer-admin to standard src/ layout | done | medium | simple | ace-linux-1 | - | aceengineer-admin | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-347 | Rename aceengineer-website/src/ to content/ | done | medium | simple | ace-linux-1 | - | aceengineer-website | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-348 | Add root pyproject.toml to workspace-hub src/ | done | medium | simple | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-349 | Document client/portfolio repos in ecosystem docs | done | low | simple | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-350 | Fix pre-existing test failures in assetutilities | archived | medium | medium | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-351 | Assign workstation to all pending/working/blocked WRK items + bake into planning workflow | archived | high | medium | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | ⏳ pending | - |
| WRK-352 | Set up remote desktop access on ace-linux-2 | working | low | simple | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ██░ 95% | n/a | - |
| WRK-353 | Expand S-N curve library from 17 to 20 standards | done | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-354 | Structural module — implement jacket and topside analysis | done | high | high | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-355 | Pipeline and flexibles module — pressure containment checks | done | medium | high | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-356 | CP module — sacrificial anode design full calculations per DNV-RP-B401 | done | medium | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-357 | Extract offshore vessel fleet data from Offshore Magazine survey PDFs | archived | medium | medium | ace-linux-1 | - | frontierdeepwater | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-358 | Enrich vessel fleet data with online research — current fleet status + newer surveys | archived | medium | high | ace-linux-1 | - | frontierdeepwater | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | WRK-357 |
| WRK-359 | Design and build vessel marine-parameters database for engineering analysis | archived | medium | high | ace-linux-1 | - | frontierdeepwater | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | WRK-358 |
| WRK-360 | Extract contractor contact data + build offshore contractor BD call list | archived | high | medium | ace-linux-1 | - | frontierdeepwater, aceengineer-admin | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-361 | Heriberto: powder room sink caulk for water drainage | in_progress | medium | simple | ace-linux-1 | - | achantas-data | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-363 | Audit and deploy cron schedules across all workstations — comprehensive-learning, session-analysis, model-ids, skills-curation | done | high | medium | ace-linux-1 | - | - | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-364 | Delete Windows-path directory artifacts in digitalmodel and worldenergydata | archived | high | simple | - | - | digitalmodel, worldenergydata | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-365 | worldenergydata root cleanup — modules/, validators/, tests/agent_os/ | archived | medium | simple | - | - | worldenergydata | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-366 | assethold root cleanup — .agent-os/, business/, agents/, empty dirs | archived | medium | medium | - | - | assethold | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-367 | assetutilities src/ cleanup — orphaned src/modules/ and src/validators/ | archived | medium | simple | - | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | WRK-351 |
| WRK-368 | Create repo-structure skill — canonical source layout for all tier-1 repos | archived | medium | simple | - | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-369 | Remove agent_os references from digitalmodel .claude/ infrastructure | archived | low | simple | - | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-370 | Heriberto: garage fence door repair | pending | medium | simple | ace-linux-1 | - | achantas-data | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-371 | Heriberto: powder room faucet tightening | pending | medium | simple | ace-linux-1 | - | achantas-data | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-372 | AI-engineering software interface skills — map and build skills AI agents need to drive engineering programs | archived | high | complex | ace-linux-2 | claude | workspace-hub, digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ██░ 90% | n/a | - |
| WRK-373 | Vision document — bridge current repo mission to autonomous-production future | archived | medium | complex | ace-linux-1 | - | workspace-hub | - | ❌ | ✅ | ❌ | ✅ | ██░ 80% | ✅ synced | - |
| WRK-374 | Personal habit — get to the point immediately when asking leaders questions | archived | high | simple | ace-linux-1 | - | - | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-375 | Incorporate SPE Drillbotics mission into ACE Engineering vision and strategy | archived | medium | medium | ace-linux-1 | - | workspace-hub, digitalmodel | - | ❌ | ❌ | ❌ | ✅ | ███ 100% | ✅ synced | - |
| WRK-376 | Casing/tubing triaxial stress design envelope check (von Mises, API DF, anisotropic grades) | done | medium | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | ⏳ pending | - |
| WRK-377 | ROP prediction model — Bourgoyne-Young and Warren in digitalmodel | archived | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ✅ | ███ 100% | ⏳ pending | - |
| WRK-378 | Generalise CT hydraulics to full wellbore hydraulics module in digitalmodel | done | high | simple | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | ⏳ pending | - |
| WRK-379 | Drilling dysfunction detector — stick-slip, washout, bit balling, kick logic | done | medium | simple | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-380 | Multi-physics simulation chain — Gmsh → OpenFOAM → OrcaFlex as agent-executable pipeline | done | medium | complex | ace-linux-1 | - | workspace-hub, digitalmodel | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | ⏳ pending | - |
| WRK-381 | Trust architecture document — formalise plan gate governance for agent-executed actions | done | medium | simple | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-382 | Marketing follow-up — update digitalmodel brochure and aceengineer-website for WRK-373/375 outputs | done | low | simple | ace-linux-1 | - | digitalmodel, aceengineer-website | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-383 | Standards-to-Module Capability Map — doc → repo → module linkage | done | high | medium | ace-linux-1 | - | workspace-hub, digitalmodel, worldenergydata, assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-384 | digitalmodel Module Registry — structured metadata for agent-callable modules | done | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-385 | Superintelligent Engineering Agent Architecture — canonical vision and blueprint | done | high | medium | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-386 | Automated Gap-to-WRK Generator — doc → module gaps spawn new work items | done | medium | medium | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-387 | Claude Code session auto-refresh with WRK context persistence | done | high | complex | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-388 | GIS skills — QGIS, Google Earth Engine, Python GIS ecosystem | done | medium | complex | ace-linux-2 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-389 | fix(ace-linux-2): switch Claude install from sudo-npm to native installer | pending | medium | medium | ace-linux-2 | - | - | - | ❌ | ❌ | ❌ | ❌ | - | - | - |
| WRK-390 | enhance(work-queue): richer WRK item presentation in work skill | done | low | medium | ace-linux-1 | - | - | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | - | - |
| WRK-392 | feat(skills): add work-document-and-exit skill — capture WRK state + session handoff | done | low | simple | ace-linux-1 | - | - | - | ❌ | ❌ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-393 | Evaluate Polymathic AI — The Well for ecosystem integration | done | medium | medium | ace-linux-2, ace-linux-1 | - | workspace-hub | - | ❌ | ✅ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-394 | Planing hull motion model — nonlinear 2D+t strip theory for high-speed vessels | done | low | complex | ace-linux-2 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-402 | worldenergydata test structure consolidation | done | low | simple | ace-linux-1 | - | worldenergydata | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-417 | The Well — planetswe dataset integration with worldenergydata/metocean | done | medium | medium | ace-linux-1 | - | worldenergydata, digitalmodel | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-418 | The Well — acoustic_scattering datasets for subsea NDE validation | done | medium | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-419 | The Well — shear_flow dataset for hydrodynamics ML baseline | done | medium | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ✅ | ✅ | ✅ | ███ 100% | n/a | - |
| WRK-420 | feat(assetutilities/calculations): implement ISO-TR 10400, 1st Ed (2007) Equations... — ISO TR 10400, 1st Ed (2007) Equations and calcu... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-421 | feat(assetutilities/calculations): implement API BULL 5C3 Formulas and Calculation... — API BULL 5C3 Formulas and Calculations for Casi... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-422 | feat(assetutilities/calculations): implement 5C — API TR 5C3 (2008) Technical Report on Equations... | done | high | medium | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-423 | feat(assetutilities/calculations): implement API TR 5C3 (2008) Technical Report on... — API TR 5C3 (2008) Technical Report on Equations... | done | high | medium | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-424 | feat(assetutilities/calculations): implement ISO-TR_10400,_1st_Ed_(2007)_Equations... — ISO TR 10400, 1st Ed (2007) Equations and calcu... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-425 | feat(assetutilities/calculations): implement BS15663 Pt 2 (2001) Life cycle costin... — BS15663 Pt 2 (2001) Life cycle costing   Guidan... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-426 | feat(assetutilities/calculations): implement Marine Trasportations_0030-4 — Marine Trasportations 0030 4 | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-427 | feat(assetutilities/calculations): implement AMJIG, Rev 2 (2000) Deep Water Drilli... — AMJIG, Rev 2 (2000) Deep Water Drilling Riser I... | done | high | medium | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-428 | feat(assetutilities/calculations): implement AMJIG, Rev2 (1999) Deep Water Drillin... — AMJIG, Rev2 (1999) Deep Water Drilling Riser In... | done | high | medium | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-429 | feat(assetutilities/calculations): implement rpt001-3 Deep Water Drilling Riser In... — rpt001 3 Deep Water Drilling Riser Integ Manag ... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-430 | feat(assetutilities/calculations): implement AMJIG, Rev1 (1998) Deep Water Drillin... — AMJIG, Rev1 (1998) Deep Water Drilling Riser In... | done | high | medium | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-431 | feat(assetutilities/calculations): implement os-f101[1] — os f101[1] | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-432 | feat(assetutilities/calculations): implement F101 — DNVOS F101 | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-433 | feat(assetutilities/calculations): implement BP - Riser drag dat — BP   Riser drag dat | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-434 | feat(assetutilities/calculations): implement Buoyant Riser_Shear7_Model — Buoyant Riser Shear7 Model | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-435 | feat(assetutilities/calculations): implement TNE011-1 Overestimation of VIV Fatigu... — TNE011 1 Overestimation of VIV Fatigue Damage f... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-436 | feat(assetutilities/calculations): implement TNE012-1 Internal Pressure Effects on... — TNE012 1 Internal Pressure Effects on Riser Ext... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-437 | feat(assetutilities/calculations): implement BP Riser Array Design Guidelines v2 — BP Riser Array Design Guidelines v2 | done | high | medium | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-438 | feat(assetutilities/calculations): implement Riser Equivalencing & De-equivalencing — Riser Equivalencing & De equivalencing | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-439 | feat(assetutilities/calculations): implement TNE011-1 Overestimation of VIV Fatigu... — TNE011 1 Overestimation of VIV Fatigue Damage f... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-440 | feat(assetutilities/calculations): implement Overestimation of VIV Fatigue Damage ... — Overestimation of VIV Fatigue Damage for Single... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-441 | feat(assetutilities/calculations): implement TNE004-1 Riser Tow Out Analysis Metho... — TNE004 1 Riser Tow Out Analysis Methodology | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-442 | feat(assetutilities/calculations): implement Huse, E., Experimental Investigation ... — Huse, E., Experimental Investigation of Deep Se... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-443 | feat(assetutilities/calculations): implement Norton, D.J., et al, 1981 - Wind Tunn... — Norton, D.J., et al, 1981   Wind Tunnel Tests o... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-444 | feat(assetutilities/calculations): implement Vandiver, J.K., et al, 1987 - Hydrody... — Vandiver, J.K., et al, 1987   Hydrodynamic Damp... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-445 | feat(assetutilities/calculations): implement Smith, C.S., et al, 1981 - Residual S... — Smith, C.S., et al, 1981   Residual Strength an... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-446 | feat(assetutilities/calculations): implement Javanmardi, K., et al, 1995 - Auger T... — Javanmardi, K., et al, 1995   Auger TLP Well Sy... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-447 | feat(assetutilities/calculations): implement Fox, S.A., et al, 1995 - Design Analy... — Fox, S.A., et al, 1995   Design Analysis and Fu... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-448 | feat(assetutilities/calculations): implement Larimore, D., et al, 1998 - Case Hist... — Larimore, D., et al, 1998   Case History   Firs... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-449 | feat(assetutilities/calculations): implement Allen, D.W., 1995 - Vortex-InducedVib... — Allen, D.W., 1995   Vortex InducedVibration Ana... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-450 | feat(assetutilities/calculations): implement Brooks, I.H., 1987 - A Pragmatic Appr... — Brooks, I.H., 1987   A Pragmatic Approach to Vo... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-451 | feat(assetutilities/calculations): implement Carminati, J.R., et al, 1999 - Ursa T... — Carminati, J.R., et al, 1999   Ursa TLP Well Sy... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-452 | feat(assetutilities/calculations): implement Barton, D.R., et al, 1999 - Genesis P... — Barton, D.R., et al, 1999   Genesis Project   D... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-453 | feat(assetutilities/calculations): implement OTC1997-8494 Code Conflicts — OTC1997 8494 Code Conflicts | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-454 | feat(assetutilities/calculations): implement OTC2001-13109 SCR Fatigue at Low KC — OTC2001 13109 SCR Fatigue at Low KC | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-455 | feat(assetutilities/calculations): implement Chen, W.C. 1989, Fatigue - Life Predi... — Chen, W.C. 1989, Fatigue   Life Predictions for... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-456 | feat(assetutilities/calculations): implement Sweeney, T., et al, 1991 - Behaviour ... — Sweeney, T., et al, 1991   Behaviour of 15ksi S... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-457 | feat(assetutilities/calculations): implement Berner, P., et al, 1997 - Neptune Pro... — Berner, P., et al, 1997   Neptune Project   Pro... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-458 | feat(assetutilities/calculations): implement Stahl, OTC 3902, Design Methodology f... — Stahl, OTC 3902, Design Methodology for Offshor... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-459 | feat(assetutilities/calculations): implement Gardner, T.N., et al, 1982 - Deepwate... — Gardner, T.N., et al, 1982   Deepwater Drilling... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-460 | feat(assetutilities/calculations): implement Allen, D.W., 1998 - Vortex-Induced Vi... — Allen, D.W., 1998   Vortex Induced Vibration of... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-461 | feat(assetutilities/calculations): implement Kim, Y.Y., et al, 1975 - Analysis of ... — Kim, Y.Y., et al, 1975   Analysis of Simultaneo... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-462 | feat(assetutilities/calculations): implement Grant, R., 1977 - Riser Fairing for R... — Grant, R., 1977   Riser Fairing for Reduced Dra... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-463 | feat(assetutilities/calculations): implement Jacobsen, V., et al, 1996 - Vibration... — Jacobsen, V., et al, 1996   Vibration Suppressi... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-464 | feat(assetutilities/calculations): implement D'Souza, R., et al, 2002 - The Next G... — D'Souza, R., et al, 2002   The Next Generation ... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-465 | feat(assetutilities/calculations): implement Vandiver, J.K., 1985 - The Prediction... — Vandiver, J.K., 1985   The Prediction of Lockin... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-466 | feat(assetutilities/calculations): implement Denison, E.B., et al, 1997 - Mars TLP... — Denison, E.B., et al, 1997   Mars TLP Drilling ... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-467 | feat(assetutilities/calculations): implement Britton, J.S., et al, 1987 - Improvin... — Britton, J.S., et al, 1987   Improving Wellhead... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-468 | feat(assetutilities/calculations): implement Miller, J.E., et al, 1985 - Influence... — Miller, J.E., et al, 1985   Influence of Mud Co... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-469 | feat(assetutilities/calculations): implement Imas, L., et al - Sensitivity of SCR ... — Imas, L., et al   Sensitivity of SCR Response a... | done | high | low | ace-linux-1 | - | assetutilities | - | ❌ | ❌ | ❌ | ❌ | ███ 100% | n/a | - |
| WRK-470 | feat(gtm): oil-and-gas practitioner persona + 1-month GTM plan for workspace-hub ecosystem | pending | high | medium | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | - | ⏳ pending | - |
| WRK-471 | fix(ace-linux-2): gemini CLI fails on Node 18 with /v regex flag | archived | high | simple | ace-linux-2 | - | workspace-hub | - | ❌ | ❌ | ✅ | ❌ | ███ 100% | ⏳ pending | - |
| WRK-473 | feat(hydrodynamics): integrate wavespectra library for spectral processing | pending | medium | simple | - | - | digitalmodel | hydrodynamics/wave_spectra | ❌ | ✅ | ❌ | ❌ | - | n/a | - |
| WRK-474 | feat(subsea): integrate MoorDyn + MoorPy for mooring analysis | pending | medium | moderate | - | - | digitalmodel | subsea/mooring_analysis | ❌ | ✅ | ❌ | ❌ | - | n/a | - |
| WRK-475 | feat(marine_ops): wire Open-Meteo Marine API into weather-window module | pending | medium | simple | - | - | digitalmodel | marine_ops/marine_analysis | ❌ | ✅ | ❌ | ❌ | - | n/a | - |
| WRK-476 | feat(worldenergydata): create ESG/Carbon Emissions module | pending | high | moderate | - | - | worldenergydata | esg_carbon | ❌ | ✅ | ❌ | ❌ | - | n/a | - |
| WRK-477 | feat(worldenergydata): create Offshore Geohazard Feed module using USGS API | pending | medium | simple | - | - | worldenergydata | safety_analysis/geohazard | ❌ | ✅ | ❌ | ❌ | - | n/a | - |
| WRK-478 | feat(subsea): create Cathodic Protection module (DNV-RP-B401) | pending | high | moderate | - | - | digitalmodel | subsea/cp_analysis | ❌ | ✅ | ❌ | ❌ | - | n/a | - |
| WRK-479 | feat(worldenergydata): wire SODIR FactPages OData API | pending | medium | moderate | - | - | worldenergydata | sodir | ❌ | ✅ | ❌ | ❌ | - | n/a | - |
| WRK-480 | feat(worldenergydata): integrate CMEMS Wave Multi-Year Product | pending | medium | moderate | - | - | worldenergydata | metocean | ❌ | ✅ | ❌ | ❌ | - | n/a | - |
| WRK-481 | feat(digitalmodel): integrate GEBCO_2025 Bathymetry for subsea routing | pending | high | moderate | - | - | digitalmodel | subsea | ❌ | ✅ | ❌ | ❌ | - | n/a | - |
| WRK-482 | feat(digitalmodel/cathodic_protection): Implement API RP 1632 — API RP 1632 Cathodic Protection of Underground Pet | pending | high | high | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-483 | feat(digitalmodel/cathodic_protection): Implement ASTM G80 — ASTM G80 (1998) Std Test Method for Specific Catho | pending | medium | low | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-484 | feat(digitalmodel/cathodic_protection): Implement ASTM G42 — ASTM G42 (1996) Std Test Method for Cathodic Disbo | pending | medium | low | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-485 | feat(digitalmodel/cathodic_protection): Implement ASTM G95 — ASTM G95 (1998) Std Test Method for Cathodic Disbo | pending | medium | low | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-486 | feat(digitalmodel/cathodic_protection): Implement ASTM G8 — ASTM G8 (1996) Std Test Methods for Cathodic Disbo | pending | medium | low | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-487 | feat(digitalmodel/cathodic_protection): Implement ASTM G110 — ASTM G110 (2003) Std Practice for Evaluating Inter | pending | medium | low | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-488 | feat(digitalmodel/cathodic_protection): Implement ISO 15156 — ISO 15156 Pt 3 1st Ed (2003) Cracking-resistant CR | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-489 | feat(digitalmodel/cathodic_protection): Implement ISO 11881 — ISO 11881 1st Ed (1999) Corrosion of metals and al | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-490 | feat(digitalmodel/cathodic_protection): Implement ISO 11881 — ISO 11881 Corrigendum 1 (1999) Corrosion of metals | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-491 | feat(digitalmodel/cathodic_protection): Implement ISO 15589-2 — ISO15589-2-2004forOR Cathodic Protection | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-492 | feat(digitalmodel/cathodic_protection): Implement ISO 11846 — ISO 11846 1st Ed (1995) Corrosion of metals and al | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-493 | feat(digitalmodel/cathodic_protection): Implement DNV F103 — DNV RP F103 (2010) Cathodic Protection of Submarin | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-494 | feat(digitalmodel/cathodic_protection): Implement DNV F106 — DNV RP F106 (2003) Factory Applied External Pipeli | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-495 | feat(digitalmodel/cathodic_protection): Implement DNV B401 — DNV RP B401 with 2008 amendments (2005) Cathodic P | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-496 | feat(digitalmodel/cathodic_protection): Implement DNV F112 — DNV RP F112 (2008) Stainless steel subsea equipmen | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-497 | feat(digitalmodel/pipeline): Implement API RP 1111 — API RP 1111 | pending | high | high | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-498 | feat(doris/pipeline): Implement API RP 1111 — API RP 1111 | pending | high | high | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-499 | feat(digitalmodel/pipeline): Implement API RP 1109 — API RP 1109 Marking Liquid Petroleum Pipeline Faci | pending | high | high | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-500 | feat(doris/pipeline): Implement API RP 1109 — API RP 1109 Marking Liquid Petroleum Pipeline Faci | pending | high | high | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-501 | feat(digitalmodel/pipeline): Implement ISO 16708 — ISO 16708 1st Ed (2006) Pipeline transportation se | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-502 | feat(doris/pipeline): Implement ISO 16708 — ISO 16708 1st Ed (2006) Pipeline transportation se | pending | high | medium | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-503 | feat(digitalmodel/pipeline): Implement ISO 13628 — ISO 13628 Pt 7 DRAFT (2003) Completion workover ri | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-504 | feat(doris/pipeline): Implement ISO 13628 — ISO 13628 Pt 7 DRAFT (2003) Completion workover ri | pending | high | medium | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-505 | feat(digitalmodel/pipeline): Implement ISO 13624-1 — DIN EN ISO 13624-1 (2007-11) Risers | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-506 | feat(doris/pipeline): Implement ISO 13624-1 — DIN EN ISO 13624-1 (2007-11) Risers | pending | high | medium | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-507 | feat(digitalmodel/pipeline): Implement ISO 13628-7 — ISO 13628-7 2005 Completion Workover Risers | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-508 | feat(doris/pipeline): Implement ISO 13628-7 — ISO 13628-7 2005 Completion Workover Risers | pending | high | medium | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-509 | feat(digitalmodel/pipeline): Implement ISO 16389 — ISO 16389 (2003) Dynamic Risers for Floating Produ | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-510 | feat(doris/pipeline): Implement ISO 16389 — ISO 16389 (2003) Dynamic Risers for Floating Produ | pending | high | medium | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-511 | feat(digitalmodel/pipeline): Implement API STD 2RD — API STD 2RD 2nd Ed (2013) Dynamic Risers for Float | pending | high | high | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-512 | feat(doris/pipeline): Implement API STD 2RD — API STD 2RD 2nd Ed (2013) Dynamic Risers for Float | pending | high | high | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-513 | feat(digitalmodel/pipeline): Implement DNV F101 — DNV OS F101 (2010) Submarine Pipeline Systems | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-514 | feat(doris/pipeline): Implement DNV F101 — DNV OS F101 (2010) Submarine Pipeline Systems | pending | high | medium | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-515 | feat(digitalmodel/pipeline): Implement API RP 17G — API RP 17G 2nd Ed (2006) Design and Operation of C | pending | high | high | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-516 | feat(doris/pipeline): Implement API RP 17G — API RP 17G 2nd Ed (2006) Design and Operation of C | pending | high | high | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-517 | feat(digitalmodel/pipeline): Implement DNV OSS 006 — DNV OSS 006 (1981) Rules for Submarine Pipeline Sy | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-518 | feat(doris/pipeline): Implement DNV OSS 006 — DNV OSS 006 (1981) Rules for Submarine Pipeline Sy | pending | high | medium | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-519 | feat(digitalmodel/pipeline): Implement DNV F201 — DNV OS F201 (2010) Dynamic Risers | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-520 | feat(doris/pipeline): Implement DNV F201 — DNV OS F201 (2010) Dynamic Risers | pending | high | medium | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-521 | feat(digitalmodel/pipeline): Implement DNV F110 — DNV RP F110 (2007) Global buckling of submarine pi | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-522 | feat(doris/pipeline): Implement DNV F110 — DNV RP F110 (2007) Global buckling of submarine pi | pending | high | medium | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-523 | feat(digitalmodel/pipeline): Implement DNV F108 — DNV RP F108 with update 2009 (2006) Fracture Contr | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-524 | feat(doris/pipeline): Implement DNV F108 — DNV RP F108 with update 2009 (2006) Fracture Contr | pending | high | medium | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-525 | feat(digitalmodel/pipeline): Implement DNV F203 — DNV RP F203 (2009) Riser interference | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-526 | feat(doris/pipeline): Implement DNV F203 — DNV RP F203 (2009) Riser interference | pending | high | medium | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-527 | feat(digitalmodel/pipeline): Implement DNV F105 — DNV RP F105 (2006) Free Spanning Pipelines | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-528 | feat(doris/pipeline): Implement DNV F105 — DNV RP F105 (2006) Free Spanning Pipelines | pending | high | medium | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-529 | feat(digitalmodel/pipeline): Implement DNV F102 — DNV RP F102 (2011) Pipeline Field Joint Coating an | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-530 | feat(doris/pipeline): Implement DNV F102 — DNV RP F102 (2011) Pipeline Field Joint Coating an | pending | high | medium | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-531 | feat(digitalmodel/pipeline): Implement DNV F202 — DNV RP F202 (2010) Composite Risers | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-532 | feat(doris/pipeline): Implement DNV F202 — DNV RP F202 (2010) Composite Risers | pending | high | medium | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-533 | feat(digitalmodel/pipeline): Implement DNV F206 — DNV RP F206 (2008) Riser Integrity Management | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-534 | feat(doris/pipeline): Implement DNV F206 — DNV RP F206 (2008) Riser Integrity Management | pending | high | medium | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-535 | feat(digitalmodel/pipeline): Implement DNV F109 — DNV RP F109 (2007) On-bottom stability design of s | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-536 | feat(doris/pipeline): Implement DNV F109 — DNV RP F109 (2007) On-bottom stability design of s | pending | high | medium | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-537 | feat(digitalmodel/pipeline): Implement DNV F116 — DNV RP F116 (2009) Integrity Management of Submari | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-538 | feat(doris/pipeline): Implement DNV F116 — DNV RP F116 (2009) Integrity Management of Submari | pending | high | medium | ace-linux-1 | - | doris | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-539 | feat(digitalmodel/structural): Implement API RP 2A — API RP 2A WSD | pending | high | high | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-540 | feat(OGManufacturing/structural): Implement API RP 2A — API RP 2A WSD | pending | high | high | ace-linux-1 | - | OGManufacturing | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-541 | feat(digitalmodel/structural): Implement ASTM A131 — ASTM A131 (2004) Std Specification for Structural  | pending | medium | low | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-542 | feat(OGManufacturing/structural): Implement ASTM A131 — ASTM A131 (2004) Std Specification for Structural  | pending | medium | low | ace-linux-1 | - | OGManufacturing | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-543 | feat(digitalmodel/structural): Implement ASTM E1049 — ASTM E1049-85(2005) Standard Practices for Cycle C | pending | high | low | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-544 | feat(OGManufacturing/structural): Implement ASTM E1049 — ASTM E1049-85(2005) Standard Practices for Cycle C | pending | high | low | ace-linux-1 | - | OGManufacturing | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-545 | feat(digitalmodel/structural): Implement ASTM E606 — ASTM E606 (2004) Std Practice for Strain-Controlle | pending | medium | low | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-546 | feat(OGManufacturing/structural): Implement ASTM E606 — ASTM E606 (2004) Std Practice for Strain-Controlle | pending | medium | low | ace-linux-1 | - | OGManufacturing | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-547 | feat(digitalmodel/structural): Implement ASTM E647 — ASTM E647 (2005) Std Test Method for Measurement o | pending | high | low | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-548 | feat(OGManufacturing/structural): Implement ASTM E647 — ASTM E647 (2005) Std Test Method for Measurement o | pending | high | low | ace-linux-1 | - | OGManufacturing | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-549 | feat(digitalmodel/structural): Implement ASTM E466 — ASTM E466 (2002) Std Practice for Conducting Force | pending | medium | low | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-550 | feat(OGManufacturing/structural): Implement ASTM E466 — ASTM E466 (2002) Std Practice for Conducting Force | pending | medium | low | ace-linux-1 | - | OGManufacturing | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-551 | feat(digitalmodel/structural): Implement ASTM E739 — ASTM E739 (2004) Std Practice for Statistical Anal | pending | medium | low | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-552 | feat(OGManufacturing/structural): Implement ASTM E739 — ASTM E739 (2004) Std Practice for Statistical Anal | pending | medium | low | ace-linux-1 | - | OGManufacturing | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-553 | feat(digitalmodel/structural): Implement ASTM A36 — ASTM A36M-04 (2004) Standard Specification for Car | pending | medium | low | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-554 | feat(OGManufacturing/structural): Implement ASTM A36 — ASTM A36M-04 (2004) Standard Specification for Car | pending | medium | low | ace-linux-1 | - | OGManufacturing | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-555 | feat(digitalmodel/marine): Implement DNV E301 — DNV OS E301 (2010) Position Mooring | pending | high | medium | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-556 | feat(digitalmodel/marine): Implement API RP 2I — API RP 2I 3rd Ed (2008) In-service Inspection of M | pending | high | high | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-557 | feat(digitalmodel/marine): Implement API RP 572 — API RP 572 2nd Ed (2001) Inspection of Pressure Ve | pending | high | high | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-558 | feat(digitalmodel/marine): Implement API RP 2SM — API RP 2SM 1st Ed & Addendum (2001 & 2007) Design, | pending | high | high | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-559 | feat(digitalmodel/marine): Implement API RP 2P — API RP 2P 2nd Ed (1987) Analysis of Spread Mooring | pending | high | high | ace-linux-1 | - | digitalmodel | - | ❌ | ❌ | ❌ | ❌ | - | n/a | - |
| WRK-TEST-ENSEMBLE | Smoke test for ensemble planning | pending | low | simple | ace-linux-1 | - | workspace-hub | - | ❌ | ❌ | ❌ | ❌ | - | - | - |

## By Status

### Done (unarchived)

| ID | Title | Priority | Complexity | Repos | Module |
|-----|-------|----------|------------|-------|--------|
| WRK-019 | Establish drilling, completion, and intervention cost data by region and environment | low | complex | worldenergydata | - |
| WRK-022 | US property valuation analysis using GIS — location, traffic, and spatial factors | medium | complex | assethold | - |
| WRK-041 | Develop long-term plan for Hobbies repo | low | medium | hobbies | - |
| WRK-042 | Develop long-term plan for Investments repo | low | medium | investments | - |
| WRK-080 | Write 4 energy data blog posts for SEO | low | complex | aceengineer-website | - |
| WRK-081 | Build interactive NPV calculator for website lead generation | low | complex | aceengineer-website | - |
| WRK-085 | Create public sample data access page on website | low | medium | aceengineer-website | - |
| WRK-101 | Add mesh decimation/coarsening to mesh-utilities skill | low | medium | digitalmodel | - |
| WRK-106 | Hull panel geometry generator from waterline, section, and profile line definitions | medium | complex | digitalmodel | - |
| WRK-112 | Appliance lifecycle analytics module for assethold | medium | complex | assethold | - |
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | high | complex | digitalmodel | - |
| WRK-141 | Create Achantas family tree to connect all family members | medium | medium | achantas-data | - |
| WRK-146 | Overhaul aceengineer-website: fix positioning, narrative, and social proof | high | complex | aceengineer-website | - |
| WRK-147 | Set up aceengineer-strategy private repo with business operations framework | high | complex | aceengineer-strategy | - |
| WRK-150 | assetutilities test coverage improvement (re-creates WRK-052) | medium | medium | assetutilities | - |
| WRK-156 | FFS Phase 1 — wall thickness grid input with Level 1/2 accept-reject workflow | high | complex | digitalmodel | asset_integrity |
| WRK-165 | Research subsea intervention analysis opportunities | medium | medium | digitalmodel, worldenergydata | subsea_intervention |
| WRK-166 | Jabra USB dongle lost — research universal dongle compatibility | medium | simple | - | - |
| WRK-167 | Calendar: Krishna ADHD evaluation — 24 Feb 2:30 PM | high | simple | - | - |
| WRK-169 | Drilling technology evolution — MPD adoption case study | medium | medium | aceengineer-website, worldenergydata | content |
| WRK-173 | Session Management Workflow Documentation + Schematic | high | low | workspace-hub | - |
| WRK-175 | Session Start: Engineering Context Loader | medium | medium | workspace-hub | - |
| WRK-176 | Session Start: Design Code Version Guard | high | low | workspace-hub, digitalmodel | - |
| WRK-183 | Domain Knowledge Graph | medium | high | workspace-hub, worldenergydata, digitalmodel | - |
| WRK-191 | Field development case study catalog — structured reference library of real projects | medium | moderate | digitalmodel | field_development_references |
| WRK-192 | Field development schematic generator — Python SVG/PNG layout diagrams | medium | complex | digitalmodel | field_development_visuals |
| WRK-197 | Nigeria NUPRC + EITI data framework — West Africa deepwater and multi-country payment data | low | moderate | worldenergydata | west_africa |
| WRK-198 | HSE risk index interactive web dashboard | medium | complex | aceengineer-website | demos/hse-risk-dashboard.html |
| WRK-199 | AI agent usage optimizer skill — maximize Claude/Codex/Gemini allocation per task | medium | medium | workspace-hub | ai-tools |
| WRK-209 | Add unit validator to EnvironmentSpec.water_density — catch physically implausible values | medium | small | digitalmodel | - |
| WRK-221 | Offshore resilience design framework — modular platforms, lifecycle planning, structural monitoring | low | medium | digitalmodel, aceengineer-website | offshore_resilience |
| WRK-224 | Tool-readiness SKILL.md — session-start check for CLI, data sources, statusline, work queue | medium | low | workspace-hub | - |
| WRK-226 | Audit and improve agent performance files across Claude, Codex, and Gemini | high | medium | workspace-hub | - |
| WRK-228 | Cross-machine terminal UX consistency — Windows Git Bash vs Linux terminal | high | medium | - | - |
| WRK-229 | AI agent QA closure — HTML output + SME verification loop per work item | high | medium | - | - |
| WRK-229 | Skills curation — online research, knowledge graph review, update index, session-input health check | high | medium | workspace-hub | - |
| WRK-236 | Test health trends — track test-writing pairing with code-writing sessions | medium | medium | workspace-hub | - |
| WRK-237 | Provider cost tracking — token spend per session and per WRK item | medium | medium | workspace-hub | - |
| WRK-238 | Adopt Codex 0.102.0 TOML role definitions — implement native multi-agent roles in .codex/ | medium | medium | workspace-hub | - |
| WRK-251 | Dynacard vision model evaluation — benchmark GPT-4V / Claude Vision vs current heuristics | medium | medium | digitalmodel | - |
| WRK-253 | Data residence tier compliance audit and extension to assethold | medium | medium | worldenergydata, digitalmodel, assethold | - |
| WRK-254 | Heavy vessel GIS integration — connect vessel dataset to GIS skill and BSEE pipeline | medium | medium | worldenergydata, digitalmodel | - |
| WRK-257 | Agent coordination model ADR — document architectural decision record | low | simple | workspace-hub | - |
| WRK-262 | Add path-handling guidance to session preflight hook | low | simple | workspace-hub | - |
| WRK-263 | Progressively reduce agent harness files to ~20 lines by migrating content to skills | high | medium | workspace-hub | - |
| WRK-264 | Ensure full work-queue workflow parity between Claude and Codex CLI | low | medium | workspace-hub | - |
| WRK-273 | CP marketing brochure — cathodic protection capability document for aceengineer-website | low | simple | digitalmodel, aceengineer-website | - |
| WRK-280 | ABS standards acquisition: create folder + download CP Guidance Notes | high | simple | workspace-hub | - |
| WRK-281 | Fix 2H legacy project discoverability (navigation layer) | medium | simple | workspace-hub | - |
| WRK-286 | Harden chore: commits — require WRK ref for multi-file changes | medium | simple | workspace-hub | - |
| WRK-288 | Finish ace-linux-2 setup — install open source engineering programs and map capabilities | low | simple | workspace-hub | - |
| WRK-289 | Research open source FEA programs for engineering assignments | low | medium | workspace-hub | - |
| WRK-290 | Install core engineering suite on ace-linux-2 (Blender, OpenFOAM, FreeCAD, Gmsh, BemRosetta) | medium | medium | workspace-hub | - |
| WRK-291 | Install recommended FEA programs on ace-linux-2 | low | medium | workspace-hub | - |
| WRK-292 | Create capability map — file formats, workflow pipelines, interoperability matrix | low | medium | workspace-hub | - |
| WRK-293 | SMART health check on ace-linux-2 drives — install smartmontools + run diagnostics | high | simple | workspace-hub | - |
| WRK-295 | Bidirectional SSH key auth between ace-linux-1 and ace-linux-2 | high | simple | workspace-hub | - |
| WRK-296 | Install Tailscale VPN on ace-linux-2 — match ace-linux-1 remote access | medium | simple | workspace-hub | - |
| WRK-298 | Install smartmontools on ace-linux-1 + SMART health check on all drives | high | simple | workspace-hub | - |
| WRK-301 | fix: recurring Write correction pattern — not responding to improve | medium | medium | - | - |
| WRK-302 | fix: recurring Edit correction pattern — not responding to improve | medium | medium | - | - |
| WRK-304 | cleanup: one lean Stop hook — consume-signals.sh only, all analysis to nightly cron | high | medium | - | - |
| WRK-305 | feat: session signal emitters — wire /clear, plan-mode, per-WRK tool-counts | medium | medium | - | - |
| WRK-306 | feat: AI agent readiness check — claude/codex/gemini CLI versions + default models | medium | medium | - | - |
| WRK-307 | track: lean-session hook requirement missed — accountability record | high | medium | - | - |
| WRK-308 | perf: move pre-commit skill validation + readiness checks to nightly cron | high | medium | - | - |
| WRK-313 | feat: new-machine setup guide + bootstrap script — statusline, CLI parity, cron jobs | high | medium | - | - |
| WRK-314 | OrcaFlex Reporting Phase 4 — OrcFxAPI Integration | high | medium | - | - |
| WRK-315 | CALM buoy mooring fatigue — spectral fatigue from OrcaFlex time-domain output | medium | high | digitalmodel | - |
| WRK-316 | NDBC buoy data ingestion for metocean wave scatter matrices | medium | medium | worldenergydata, digitalmodel | - |
| WRK-317 | Integrated web dashboard — Plotly Dash for BSEE and FDAS data | medium | high | worldenergydata | - |
| WRK-319 | Real-time EIA and IEA feed ingestion — weekly crude and gas production | medium | medium | worldenergydata | - |
| WRK-320 | MAIB and NTSB incident correlation with USCG MISLE for root-cause taxonomy | low | high | worldenergydata | - |
| WRK-321 | Field development economics — MIRR NPV with carbon cost sensitivity | medium | medium | worldenergydata | - |
| WRK-322 | Fundamentals scoring — P/E P/B EV/EBITDA ranking from yfinance | high | medium | assethold | - |
| WRK-323 | Covered call analyser — option chain ingestion and premium yield calculator | medium | medium | assethold | - |
| WRK-324 | Risk metrics — VaR CVaR Sharpe ratio max drawdown per position and portfolio | high | medium | assethold | - |
| WRK-325 | Sector exposure tracker — auto-classify holdings by GICS sector and flag concentration | medium | medium | assethold | - |
| WRK-326 | Unified CLI — single ace command routing to all repo tools | medium | high | workspace-hub | - |
| WRK-327 | Shared engineering constants library — material properties unit conversions seawater properties | medium | medium | workspace-hub, digitalmodel | - |
| WRK-328 | Agent-readable specs index — YAML index of all specs consumable by AI agents | medium | medium | workspace-hub | - |
| WRK-329 | Formalise doris calculation workflow — migrate ad-hoc calcs to Python modules | medium | high | doris | - |
| WRK-330 | DNV-ST-F101 pressure containment checks for subsea pipelines | medium | medium | doris | - |
| WRK-331 | API RP 1111 deepwater pipeline design checks — collapse and propagating buckle | medium | medium | doris | - |
| WRK-332 | On-bottom stability module — DNV-RP-F109 soil resistance calculations | medium | medium | doris | - |
| WRK-335 | Drilling engineering module — casing design checks per API TR 5C3 | medium | high | OGManufacturing | - |
| WRK-336 | Portable installation analysis library — extract generic OrcaFlex automation from project code | medium | high | saipem, rock-oil-field | - |
| WRK-337 | Vessel weather-window calculator — operability analysis from Hs Tp scatter | medium | medium | saipem, rock-oil-field | - |
| WRK-338 | LNG tank structural checks — API 620 and EN 14620 thin-shell hoop stress | medium | medium | acma-projects | - |
| WRK-339 | Aluminium structural module — Eurocode 9 and AA ADM member capacity checks | medium | medium | acma-projects | - |
| WRK-340 | Composite panel design tool — Classical Laminate Theory CLT strength checks | medium | high | acma-projects | - |
| WRK-341 | Review pdf-large-reader vs native AI agent PDF capabilities — assess continuation or deprecation | medium | simple | pdf-large-reader, workspace-hub | - |
| WRK-342 | Multi-machine workflow clarity — SSH helper scripts, hostname in statusline, CLI consistency across ace-linux-1 and ace-linux-2 | high | medium | workspace-hub | - |
| WRK-344 | Remove agent_os from assetutilities | high | simple | assetutilities | - |
| WRK-345 | Consolidate validators package into assetutilities | high | simple | assetutilities, worldenergydata, assethold | - |
| WRK-346 | Fix aceengineer-admin to standard src/ layout | medium | simple | aceengineer-admin | - |
| WRK-347 | Rename aceengineer-website/src/ to content/ | medium | simple | aceengineer-website | - |
| WRK-348 | Add root pyproject.toml to workspace-hub src/ | medium | simple | workspace-hub | - |
| WRK-349 | Document client/portfolio repos in ecosystem docs | low | simple | workspace-hub | - |
| WRK-353 | Expand S-N curve library from 17 to 20 standards | high | medium | digitalmodel | - |
| WRK-354 | Structural module — implement jacket and topside analysis | high | high | digitalmodel | - |
| WRK-355 | Pipeline and flexibles module — pressure containment checks | medium | high | digitalmodel | - |
| WRK-356 | CP module — sacrificial anode design full calculations per DNV-RP-B401 | medium | medium | digitalmodel | - |
| WRK-363 | Audit and deploy cron schedules across all workstations — comprehensive-learning, session-analysis, model-ids, skills-curation | high | medium | - | - |
| WRK-376 | Casing/tubing triaxial stress design envelope check (von Mises, API DF, anisotropic grades) | medium | medium | digitalmodel | - |
| WRK-378 | Generalise CT hydraulics to full wellbore hydraulics module in digitalmodel | high | simple | digitalmodel | - |
| WRK-379 | Drilling dysfunction detector — stick-slip, washout, bit balling, kick logic | medium | simple | digitalmodel | - |
| WRK-380 | Multi-physics simulation chain — Gmsh → OpenFOAM → OrcaFlex as agent-executable pipeline | medium | complex | workspace-hub, digitalmodel | - |
| WRK-381 | Trust architecture document — formalise plan gate governance for agent-executed actions | medium | simple | workspace-hub | - |
| WRK-382 | Marketing follow-up — update digitalmodel brochure and aceengineer-website for WRK-373/375 outputs | low | simple | digitalmodel, aceengineer-website | - |
| WRK-383 | Standards-to-Module Capability Map — doc → repo → module linkage | high | medium | workspace-hub, digitalmodel, worldenergydata, assetutilities | - |
| WRK-384 | digitalmodel Module Registry — structured metadata for agent-callable modules | high | medium | digitalmodel | - |
| WRK-385 | Superintelligent Engineering Agent Architecture — canonical vision and blueprint | high | medium | workspace-hub | - |
| WRK-386 | Automated Gap-to-WRK Generator — doc → module gaps spawn new work items | medium | medium | workspace-hub | - |
| WRK-387 | Claude Code session auto-refresh with WRK context persistence | high | complex | workspace-hub | - |
| WRK-388 | GIS skills — QGIS, Google Earth Engine, Python GIS ecosystem | medium | complex | workspace-hub | - |
| WRK-390 | enhance(work-queue): richer WRK item presentation in work skill | low | medium | - | - |
| WRK-392 | feat(skills): add work-document-and-exit skill — capture WRK state + session handoff | low | simple | - | - |
| WRK-393 | Evaluate Polymathic AI — The Well for ecosystem integration | medium | medium | workspace-hub | - |
| WRK-394 | Planing hull motion model — nonlinear 2D+t strip theory for high-speed vessels | low | complex | digitalmodel | - |
| WRK-402 | worldenergydata test structure consolidation | low | simple | worldenergydata | - |
| WRK-417 | The Well — planetswe dataset integration with worldenergydata/metocean | medium | medium | worldenergydata, digitalmodel | - |
| WRK-418 | The Well — acoustic_scattering datasets for subsea NDE validation | medium | medium | digitalmodel | - |
| WRK-419 | The Well — shear_flow dataset for hydrodynamics ML baseline | medium | medium | digitalmodel | - |
| WRK-420 | feat(assetutilities/calculations): implement ISO-TR 10400, 1st Ed (2007) Equations... — ISO TR 10400, 1st Ed (2007) Equations and calcu... | high | low | assetutilities | - |
| WRK-421 | feat(assetutilities/calculations): implement API BULL 5C3 Formulas and Calculation... — API BULL 5C3 Formulas and Calculations for Casi... | high | low | assetutilities | - |
| WRK-422 | feat(assetutilities/calculations): implement 5C — API TR 5C3 (2008) Technical Report on Equations... | high | medium | assetutilities | - |
| WRK-423 | feat(assetutilities/calculations): implement API TR 5C3 (2008) Technical Report on... — API TR 5C3 (2008) Technical Report on Equations... | high | medium | assetutilities | - |
| WRK-424 | feat(assetutilities/calculations): implement ISO-TR_10400,_1st_Ed_(2007)_Equations... — ISO TR 10400, 1st Ed (2007) Equations and calcu... | high | low | assetutilities | - |
| WRK-425 | feat(assetutilities/calculations): implement BS15663 Pt 2 (2001) Life cycle costin... — BS15663 Pt 2 (2001) Life cycle costing   Guidan... | high | low | assetutilities | - |
| WRK-426 | feat(assetutilities/calculations): implement Marine Trasportations_0030-4 — Marine Trasportations 0030 4 | high | low | assetutilities | - |
| WRK-427 | feat(assetutilities/calculations): implement AMJIG, Rev 2 (2000) Deep Water Drilli... — AMJIG, Rev 2 (2000) Deep Water Drilling Riser I... | high | medium | assetutilities | - |
| WRK-428 | feat(assetutilities/calculations): implement AMJIG, Rev2 (1999) Deep Water Drillin... — AMJIG, Rev2 (1999) Deep Water Drilling Riser In... | high | medium | assetutilities | - |
| WRK-429 | feat(assetutilities/calculations): implement rpt001-3 Deep Water Drilling Riser In... — rpt001 3 Deep Water Drilling Riser Integ Manag ... | high | low | assetutilities | - |
| WRK-430 | feat(assetutilities/calculations): implement AMJIG, Rev1 (1998) Deep Water Drillin... — AMJIG, Rev1 (1998) Deep Water Drilling Riser In... | high | medium | assetutilities | - |
| WRK-431 | feat(assetutilities/calculations): implement os-f101[1] — os f101[1] | high | low | assetutilities | - |
| WRK-432 | feat(assetutilities/calculations): implement F101 — DNVOS F101 | high | low | assetutilities | - |
| WRK-433 | feat(assetutilities/calculations): implement BP - Riser drag dat — BP   Riser drag dat | high | low | assetutilities | - |
| WRK-434 | feat(assetutilities/calculations): implement Buoyant Riser_Shear7_Model — Buoyant Riser Shear7 Model | high | low | assetutilities | - |
| WRK-435 | feat(assetutilities/calculations): implement TNE011-1 Overestimation of VIV Fatigu... — TNE011 1 Overestimation of VIV Fatigue Damage f... | high | low | assetutilities | - |
| WRK-436 | feat(assetutilities/calculations): implement TNE012-1 Internal Pressure Effects on... — TNE012 1 Internal Pressure Effects on Riser Ext... | high | low | assetutilities | - |
| WRK-437 | feat(assetutilities/calculations): implement BP Riser Array Design Guidelines v2 — BP Riser Array Design Guidelines v2 | high | medium | assetutilities | - |
| WRK-438 | feat(assetutilities/calculations): implement Riser Equivalencing & De-equivalencing — Riser Equivalencing & De equivalencing | high | low | assetutilities | - |
| WRK-439 | feat(assetutilities/calculations): implement TNE011-1 Overestimation of VIV Fatigu... — TNE011 1 Overestimation of VIV Fatigue Damage f... | high | low | assetutilities | - |
| WRK-440 | feat(assetutilities/calculations): implement Overestimation of VIV Fatigue Damage ... — Overestimation of VIV Fatigue Damage for Single... | high | low | assetutilities | - |
| WRK-441 | feat(assetutilities/calculations): implement TNE004-1 Riser Tow Out Analysis Metho... — TNE004 1 Riser Tow Out Analysis Methodology | high | low | assetutilities | - |
| WRK-442 | feat(assetutilities/calculations): implement Huse, E., Experimental Investigation ... — Huse, E., Experimental Investigation of Deep Se... | high | low | assetutilities | - |
| WRK-443 | feat(assetutilities/calculations): implement Norton, D.J., et al, 1981 - Wind Tunn... — Norton, D.J., et al, 1981   Wind Tunnel Tests o... | high | low | assetutilities | - |
| WRK-444 | feat(assetutilities/calculations): implement Vandiver, J.K., et al, 1987 - Hydrody... — Vandiver, J.K., et al, 1987   Hydrodynamic Damp... | high | low | assetutilities | - |
| WRK-445 | feat(assetutilities/calculations): implement Smith, C.S., et al, 1981 - Residual S... — Smith, C.S., et al, 1981   Residual Strength an... | high | low | assetutilities | - |
| WRK-446 | feat(assetutilities/calculations): implement Javanmardi, K., et al, 1995 - Auger T... — Javanmardi, K., et al, 1995   Auger TLP Well Sy... | high | low | assetutilities | - |
| WRK-447 | feat(assetutilities/calculations): implement Fox, S.A., et al, 1995 - Design Analy... — Fox, S.A., et al, 1995   Design Analysis and Fu... | high | low | assetutilities | - |
| WRK-448 | feat(assetutilities/calculations): implement Larimore, D., et al, 1998 - Case Hist... — Larimore, D., et al, 1998   Case History   Firs... | high | low | assetutilities | - |
| WRK-449 | feat(assetutilities/calculations): implement Allen, D.W., 1995 - Vortex-InducedVib... — Allen, D.W., 1995   Vortex InducedVibration Ana... | high | low | assetutilities | - |
| WRK-450 | feat(assetutilities/calculations): implement Brooks, I.H., 1987 - A Pragmatic Appr... — Brooks, I.H., 1987   A Pragmatic Approach to Vo... | high | low | assetutilities | - |
| WRK-451 | feat(assetutilities/calculations): implement Carminati, J.R., et al, 1999 - Ursa T... — Carminati, J.R., et al, 1999   Ursa TLP Well Sy... | high | low | assetutilities | - |
| WRK-452 | feat(assetutilities/calculations): implement Barton, D.R., et al, 1999 - Genesis P... — Barton, D.R., et al, 1999   Genesis Project   D... | high | low | assetutilities | - |
| WRK-453 | feat(assetutilities/calculations): implement OTC1997-8494 Code Conflicts — OTC1997 8494 Code Conflicts | high | low | assetutilities | - |
| WRK-454 | feat(assetutilities/calculations): implement OTC2001-13109 SCR Fatigue at Low KC — OTC2001 13109 SCR Fatigue at Low KC | high | low | assetutilities | - |
| WRK-455 | feat(assetutilities/calculations): implement Chen, W.C. 1989, Fatigue - Life Predi... — Chen, W.C. 1989, Fatigue   Life Predictions for... | high | low | assetutilities | - |
| WRK-456 | feat(assetutilities/calculations): implement Sweeney, T., et al, 1991 - Behaviour ... — Sweeney, T., et al, 1991   Behaviour of 15ksi S... | high | low | assetutilities | - |
| WRK-457 | feat(assetutilities/calculations): implement Berner, P., et al, 1997 - Neptune Pro... — Berner, P., et al, 1997   Neptune Project   Pro... | high | low | assetutilities | - |
| WRK-458 | feat(assetutilities/calculations): implement Stahl, OTC 3902, Design Methodology f... — Stahl, OTC 3902, Design Methodology for Offshor... | high | low | assetutilities | - |
| WRK-459 | feat(assetutilities/calculations): implement Gardner, T.N., et al, 1982 - Deepwate... — Gardner, T.N., et al, 1982   Deepwater Drilling... | high | low | assetutilities | - |
| WRK-460 | feat(assetutilities/calculations): implement Allen, D.W., 1998 - Vortex-Induced Vi... — Allen, D.W., 1998   Vortex Induced Vibration of... | high | low | assetutilities | - |
| WRK-461 | feat(assetutilities/calculations): implement Kim, Y.Y., et al, 1975 - Analysis of ... — Kim, Y.Y., et al, 1975   Analysis of Simultaneo... | high | low | assetutilities | - |
| WRK-462 | feat(assetutilities/calculations): implement Grant, R., 1977 - Riser Fairing for R... — Grant, R., 1977   Riser Fairing for Reduced Dra... | high | low | assetutilities | - |
| WRK-463 | feat(assetutilities/calculations): implement Jacobsen, V., et al, 1996 - Vibration... — Jacobsen, V., et al, 1996   Vibration Suppressi... | high | low | assetutilities | - |
| WRK-464 | feat(assetutilities/calculations): implement D'Souza, R., et al, 2002 - The Next G... — D'Souza, R., et al, 2002   The Next Generation ... | high | low | assetutilities | - |
| WRK-465 | feat(assetutilities/calculations): implement Vandiver, J.K., 1985 - The Prediction... — Vandiver, J.K., 1985   The Prediction of Lockin... | high | low | assetutilities | - |
| WRK-466 | feat(assetutilities/calculations): implement Denison, E.B., et al, 1997 - Mars TLP... — Denison, E.B., et al, 1997   Mars TLP Drilling ... | high | low | assetutilities | - |
| WRK-467 | feat(assetutilities/calculations): implement Britton, J.S., et al, 1987 - Improvin... — Britton, J.S., et al, 1987   Improving Wellhead... | high | low | assetutilities | - |
| WRK-468 | feat(assetutilities/calculations): implement Miller, J.E., et al, 1985 - Influence... — Miller, J.E., et al, 1985   Influence of Mud Co... | high | low | assetutilities | - |
| WRK-469 | feat(assetutilities/calculations): implement Imas, L., et al - Sensitivity of SCR ... — Imas, L., et al   Sensitivity of SCR Response a... | high | low | assetutilities | - |

### Pending

| ID | Title | Priority | Complexity | Repos | Module |
|-----|-------|----------|------------|-------|--------|
| WRK-005 | Clean up email using AI (when safe) | low | medium | achantas-data | - |
| WRK-008 | Upload photos from multiple devices to achantas-media | low | medium | achantas-data | - |
| WRK-032 | Modular OrcaFlex pipeline installation input with parametric campaign support | medium | complex | digitalmodel | - |
| WRK-036 | OrcaFlex structure deployment analysis - supply boat side deployment with structural loads | low | complex | acma-projects | - |
| WRK-039 | SPM project benchmarking - AQWA vs OrcaFlex | medium | complex | digitalmodel | - |
| WRK-043 | Parametric hull form analysis with RAO generation and client-facing lookup graphs | low | complex | digitalmodel | - |
| WRK-045 | OrcaFlex rigid jumper analysis - stress and VIV for various configurations | medium | complex | digitalmodel | - |
| WRK-046 | OrcaFlex drilling and completion riser parametric analysis | medium | complex | digitalmodel | - |
| WRK-048 | Blender working configurations for digitalmodel | low | medium | digitalmodel | - |
| WRK-050 | Hardware consolidation — inventory, assess, repurpose devices + dev environment readiness | medium | complex | workspace-hub | - |
| WRK-075 | OFFPIPE Integration Module — pipelay cross-validation against OrcaFlex | low | complex | digitalmodel | - |
| WRK-126 | Benchmark all example models across time domain and frequency domain with seed equivalence | high | complex | digitalmodel | - |
| WRK-140 | Integrate gmsh meshing skill into digitalmodel and solver pipelines | medium | medium | digitalmodel, workspace-hub | - |
| WRK-148 | ACE-GTM: A&CE Go-to-Market strategy stream | high | complex | aceengineer-website, aceengineer-strategy, workspace-hub | - |
| WRK-171 | Cost data calibration — sanctioned project benchmarking & multivariate cost prediction | medium | complex | worldenergydata | cost |
| WRK-219 | Batch drilling economics analysis — campaign scheduling and cost optimization | medium | medium | worldenergydata, digitalmodel | drilling_economics |
| WRK-234 | MISSION: Self-improving agent ecosystem — sessions drive skills, skills drive better sessions | high | complex | workspace-hub | - |
| WRK-259 | BSEE field economics case study — calibrated NPV/IRR with cost data foundation | medium | medium | aceengineer-website, worldenergydata | - |
| WRK-261 | BSEE field economics case study — rebuild on calibrated cost data (WRK-019 + WRK-171) | medium | medium | aceengineer-website | - |
| WRK-297 | SSHFS mounts on ace-linux-1 for ace-linux-2 drives — bidirectional file access | high | simple | workspace-hub | - |
| WRK-310 | explore: OrcFxAPI schematic capture for OrcaWave models (program screenshots) | medium | medium | digitalmodel, workspace-hub | - |
| WRK-311 | improve: QTF benchmarking for case 3.1 — charts, comparisons, and validation depth | high | medium | digitalmodel | - |
| WRK-343 | OpenFOAM technical debt and exploration — tutorials, ecosystem audit, WRK-047 refresh | medium | medium | workspace-hub, digitalmodel | - |
| WRK-370 | Heriberto: garage fence door repair | medium | simple | achantas-data | - |
| WRK-371 | Heriberto: powder room faucet tightening | medium | simple | achantas-data | - |
| WRK-389 | fix(ace-linux-2): switch Claude install from sudo-npm to native installer | medium | medium | - | - |
| WRK-470 | feat(gtm): oil-and-gas practitioner persona + 1-month GTM plan for workspace-hub ecosystem | high | medium | workspace-hub | - |
| WRK-473 | feat(hydrodynamics): integrate wavespectra library for spectral processing | medium | simple | digitalmodel | hydrodynamics/wave_spectra |
| WRK-474 | feat(subsea): integrate MoorDyn + MoorPy for mooring analysis | medium | moderate | digitalmodel | subsea/mooring_analysis |
| WRK-475 | feat(marine_ops): wire Open-Meteo Marine API into weather-window module | medium | simple | digitalmodel | marine_ops/marine_analysis |
| WRK-476 | feat(worldenergydata): create ESG/Carbon Emissions module | high | moderate | worldenergydata | esg_carbon |
| WRK-477 | feat(worldenergydata): create Offshore Geohazard Feed module using USGS API | medium | simple | worldenergydata | safety_analysis/geohazard |
| WRK-478 | feat(subsea): create Cathodic Protection module (DNV-RP-B401) | high | moderate | digitalmodel | subsea/cp_analysis |
| WRK-479 | feat(worldenergydata): wire SODIR FactPages OData API | medium | moderate | worldenergydata | sodir |
| WRK-480 | feat(worldenergydata): integrate CMEMS Wave Multi-Year Product | medium | moderate | worldenergydata | metocean |
| WRK-481 | feat(digitalmodel): integrate GEBCO_2025 Bathymetry for subsea routing | high | moderate | digitalmodel | subsea |
| WRK-482 | feat(digitalmodel/cathodic_protection): Implement API RP 1632 — API RP 1632 Cathodic Protection of Underground Pet | high | high | digitalmodel | - |
| WRK-483 | feat(digitalmodel/cathodic_protection): Implement ASTM G80 — ASTM G80 (1998) Std Test Method for Specific Catho | medium | low | digitalmodel | - |
| WRK-484 | feat(digitalmodel/cathodic_protection): Implement ASTM G42 — ASTM G42 (1996) Std Test Method for Cathodic Disbo | medium | low | digitalmodel | - |
| WRK-485 | feat(digitalmodel/cathodic_protection): Implement ASTM G95 — ASTM G95 (1998) Std Test Method for Cathodic Disbo | medium | low | digitalmodel | - |
| WRK-486 | feat(digitalmodel/cathodic_protection): Implement ASTM G8 — ASTM G8 (1996) Std Test Methods for Cathodic Disbo | medium | low | digitalmodel | - |
| WRK-487 | feat(digitalmodel/cathodic_protection): Implement ASTM G110 — ASTM G110 (2003) Std Practice for Evaluating Inter | medium | low | digitalmodel | - |
| WRK-488 | feat(digitalmodel/cathodic_protection): Implement ISO 15156 — ISO 15156 Pt 3 1st Ed (2003) Cracking-resistant CR | high | medium | digitalmodel | - |
| WRK-489 | feat(digitalmodel/cathodic_protection): Implement ISO 11881 — ISO 11881 1st Ed (1999) Corrosion of metals and al | high | medium | digitalmodel | - |
| WRK-490 | feat(digitalmodel/cathodic_protection): Implement ISO 11881 — ISO 11881 Corrigendum 1 (1999) Corrosion of metals | high | medium | digitalmodel | - |
| WRK-491 | feat(digitalmodel/cathodic_protection): Implement ISO 15589-2 — ISO15589-2-2004forOR Cathodic Protection | high | medium | digitalmodel | - |
| WRK-492 | feat(digitalmodel/cathodic_protection): Implement ISO 11846 — ISO 11846 1st Ed (1995) Corrosion of metals and al | high | medium | digitalmodel | - |
| WRK-493 | feat(digitalmodel/cathodic_protection): Implement DNV F103 — DNV RP F103 (2010) Cathodic Protection of Submarin | high | medium | digitalmodel | - |
| WRK-494 | feat(digitalmodel/cathodic_protection): Implement DNV F106 — DNV RP F106 (2003) Factory Applied External Pipeli | high | medium | digitalmodel | - |
| WRK-495 | feat(digitalmodel/cathodic_protection): Implement DNV B401 — DNV RP B401 with 2008 amendments (2005) Cathodic P | high | medium | digitalmodel | - |
| WRK-496 | feat(digitalmodel/cathodic_protection): Implement DNV F112 — DNV RP F112 (2008) Stainless steel subsea equipmen | high | medium | digitalmodel | - |
| WRK-497 | feat(digitalmodel/pipeline): Implement API RP 1111 — API RP 1111 | high | high | digitalmodel | - |
| WRK-498 | feat(doris/pipeline): Implement API RP 1111 — API RP 1111 | high | high | doris | - |
| WRK-499 | feat(digitalmodel/pipeline): Implement API RP 1109 — API RP 1109 Marking Liquid Petroleum Pipeline Faci | high | high | digitalmodel | - |
| WRK-500 | feat(doris/pipeline): Implement API RP 1109 — API RP 1109 Marking Liquid Petroleum Pipeline Faci | high | high | doris | - |
| WRK-501 | feat(digitalmodel/pipeline): Implement ISO 16708 — ISO 16708 1st Ed (2006) Pipeline transportation se | high | medium | digitalmodel | - |
| WRK-502 | feat(doris/pipeline): Implement ISO 16708 — ISO 16708 1st Ed (2006) Pipeline transportation se | high | medium | doris | - |
| WRK-503 | feat(digitalmodel/pipeline): Implement ISO 13628 — ISO 13628 Pt 7 DRAFT (2003) Completion workover ri | high | medium | digitalmodel | - |
| WRK-504 | feat(doris/pipeline): Implement ISO 13628 — ISO 13628 Pt 7 DRAFT (2003) Completion workover ri | high | medium | doris | - |
| WRK-505 | feat(digitalmodel/pipeline): Implement ISO 13624-1 — DIN EN ISO 13624-1 (2007-11) Risers | high | medium | digitalmodel | - |
| WRK-506 | feat(doris/pipeline): Implement ISO 13624-1 — DIN EN ISO 13624-1 (2007-11) Risers | high | medium | doris | - |
| WRK-507 | feat(digitalmodel/pipeline): Implement ISO 13628-7 — ISO 13628-7 2005 Completion Workover Risers | high | medium | digitalmodel | - |
| WRK-508 | feat(doris/pipeline): Implement ISO 13628-7 — ISO 13628-7 2005 Completion Workover Risers | high | medium | doris | - |
| WRK-509 | feat(digitalmodel/pipeline): Implement ISO 16389 — ISO 16389 (2003) Dynamic Risers for Floating Produ | high | medium | digitalmodel | - |
| WRK-510 | feat(doris/pipeline): Implement ISO 16389 — ISO 16389 (2003) Dynamic Risers for Floating Produ | high | medium | doris | - |
| WRK-511 | feat(digitalmodel/pipeline): Implement API STD 2RD — API STD 2RD 2nd Ed (2013) Dynamic Risers for Float | high | high | digitalmodel | - |
| WRK-512 | feat(doris/pipeline): Implement API STD 2RD — API STD 2RD 2nd Ed (2013) Dynamic Risers for Float | high | high | doris | - |
| WRK-513 | feat(digitalmodel/pipeline): Implement DNV F101 — DNV OS F101 (2010) Submarine Pipeline Systems | high | medium | digitalmodel | - |
| WRK-514 | feat(doris/pipeline): Implement DNV F101 — DNV OS F101 (2010) Submarine Pipeline Systems | high | medium | doris | - |
| WRK-515 | feat(digitalmodel/pipeline): Implement API RP 17G — API RP 17G 2nd Ed (2006) Design and Operation of C | high | high | digitalmodel | - |
| WRK-516 | feat(doris/pipeline): Implement API RP 17G — API RP 17G 2nd Ed (2006) Design and Operation of C | high | high | doris | - |
| WRK-517 | feat(digitalmodel/pipeline): Implement DNV OSS 006 — DNV OSS 006 (1981) Rules for Submarine Pipeline Sy | high | medium | digitalmodel | - |
| WRK-518 | feat(doris/pipeline): Implement DNV OSS 006 — DNV OSS 006 (1981) Rules for Submarine Pipeline Sy | high | medium | doris | - |
| WRK-519 | feat(digitalmodel/pipeline): Implement DNV F201 — DNV OS F201 (2010) Dynamic Risers | high | medium | digitalmodel | - |
| WRK-520 | feat(doris/pipeline): Implement DNV F201 — DNV OS F201 (2010) Dynamic Risers | high | medium | doris | - |
| WRK-521 | feat(digitalmodel/pipeline): Implement DNV F110 — DNV RP F110 (2007) Global buckling of submarine pi | high | medium | digitalmodel | - |
| WRK-522 | feat(doris/pipeline): Implement DNV F110 — DNV RP F110 (2007) Global buckling of submarine pi | high | medium | doris | - |
| WRK-523 | feat(digitalmodel/pipeline): Implement DNV F108 — DNV RP F108 with update 2009 (2006) Fracture Contr | high | medium | digitalmodel | - |
| WRK-524 | feat(doris/pipeline): Implement DNV F108 — DNV RP F108 with update 2009 (2006) Fracture Contr | high | medium | doris | - |
| WRK-525 | feat(digitalmodel/pipeline): Implement DNV F203 — DNV RP F203 (2009) Riser interference | high | medium | digitalmodel | - |
| WRK-526 | feat(doris/pipeline): Implement DNV F203 — DNV RP F203 (2009) Riser interference | high | medium | doris | - |
| WRK-527 | feat(digitalmodel/pipeline): Implement DNV F105 — DNV RP F105 (2006) Free Spanning Pipelines | high | medium | digitalmodel | - |
| WRK-528 | feat(doris/pipeline): Implement DNV F105 — DNV RP F105 (2006) Free Spanning Pipelines | high | medium | doris | - |
| WRK-529 | feat(digitalmodel/pipeline): Implement DNV F102 — DNV RP F102 (2011) Pipeline Field Joint Coating an | high | medium | digitalmodel | - |
| WRK-530 | feat(doris/pipeline): Implement DNV F102 — DNV RP F102 (2011) Pipeline Field Joint Coating an | high | medium | doris | - |
| WRK-531 | feat(digitalmodel/pipeline): Implement DNV F202 — DNV RP F202 (2010) Composite Risers | high | medium | digitalmodel | - |
| WRK-532 | feat(doris/pipeline): Implement DNV F202 — DNV RP F202 (2010) Composite Risers | high | medium | doris | - |
| WRK-533 | feat(digitalmodel/pipeline): Implement DNV F206 — DNV RP F206 (2008) Riser Integrity Management | high | medium | digitalmodel | - |
| WRK-534 | feat(doris/pipeline): Implement DNV F206 — DNV RP F206 (2008) Riser Integrity Management | high | medium | doris | - |
| WRK-535 | feat(digitalmodel/pipeline): Implement DNV F109 — DNV RP F109 (2007) On-bottom stability design of s | high | medium | digitalmodel | - |
| WRK-536 | feat(doris/pipeline): Implement DNV F109 — DNV RP F109 (2007) On-bottom stability design of s | high | medium | doris | - |
| WRK-537 | feat(digitalmodel/pipeline): Implement DNV F116 — DNV RP F116 (2009) Integrity Management of Submari | high | medium | digitalmodel | - |
| WRK-538 | feat(doris/pipeline): Implement DNV F116 — DNV RP F116 (2009) Integrity Management of Submari | high | medium | doris | - |
| WRK-539 | feat(digitalmodel/structural): Implement API RP 2A — API RP 2A WSD | high | high | digitalmodel | - |
| WRK-540 | feat(OGManufacturing/structural): Implement API RP 2A — API RP 2A WSD | high | high | OGManufacturing | - |
| WRK-541 | feat(digitalmodel/structural): Implement ASTM A131 — ASTM A131 (2004) Std Specification for Structural  | medium | low | digitalmodel | - |
| WRK-542 | feat(OGManufacturing/structural): Implement ASTM A131 — ASTM A131 (2004) Std Specification for Structural  | medium | low | OGManufacturing | - |
| WRK-543 | feat(digitalmodel/structural): Implement ASTM E1049 — ASTM E1049-85(2005) Standard Practices for Cycle C | high | low | digitalmodel | - |
| WRK-544 | feat(OGManufacturing/structural): Implement ASTM E1049 — ASTM E1049-85(2005) Standard Practices for Cycle C | high | low | OGManufacturing | - |
| WRK-545 | feat(digitalmodel/structural): Implement ASTM E606 — ASTM E606 (2004) Std Practice for Strain-Controlle | medium | low | digitalmodel | - |
| WRK-546 | feat(OGManufacturing/structural): Implement ASTM E606 — ASTM E606 (2004) Std Practice for Strain-Controlle | medium | low | OGManufacturing | - |
| WRK-547 | feat(digitalmodel/structural): Implement ASTM E647 — ASTM E647 (2005) Std Test Method for Measurement o | high | low | digitalmodel | - |
| WRK-548 | feat(OGManufacturing/structural): Implement ASTM E647 — ASTM E647 (2005) Std Test Method for Measurement o | high | low | OGManufacturing | - |
| WRK-549 | feat(digitalmodel/structural): Implement ASTM E466 — ASTM E466 (2002) Std Practice for Conducting Force | medium | low | digitalmodel | - |
| WRK-550 | feat(OGManufacturing/structural): Implement ASTM E466 — ASTM E466 (2002) Std Practice for Conducting Force | medium | low | OGManufacturing | - |
| WRK-551 | feat(digitalmodel/structural): Implement ASTM E739 — ASTM E739 (2004) Std Practice for Statistical Anal | medium | low | digitalmodel | - |
| WRK-552 | feat(OGManufacturing/structural): Implement ASTM E739 — ASTM E739 (2004) Std Practice for Statistical Anal | medium | low | OGManufacturing | - |
| WRK-553 | feat(digitalmodel/structural): Implement ASTM A36 — ASTM A36M-04 (2004) Standard Specification for Car | medium | low | digitalmodel | - |
| WRK-554 | feat(OGManufacturing/structural): Implement ASTM A36 — ASTM A36M-04 (2004) Standard Specification for Car | medium | low | OGManufacturing | - |
| WRK-555 | feat(digitalmodel/marine): Implement DNV E301 — DNV OS E301 (2010) Position Mooring | high | medium | digitalmodel | - |
| WRK-556 | feat(digitalmodel/marine): Implement API RP 2I — API RP 2I 3rd Ed (2008) In-service Inspection of M | high | high | digitalmodel | - |
| WRK-557 | feat(digitalmodel/marine): Implement API RP 572 — API RP 572 2nd Ed (2001) Inspection of Pressure Ve | high | high | digitalmodel | - |
| WRK-558 | feat(digitalmodel/marine): Implement API RP 2SM — API RP 2SM 1st Ed & Addendum (2001 & 2007) Design, | high | high | digitalmodel | - |
| WRK-559 | feat(digitalmodel/marine): Implement API RP 2P — API RP 2P 2nd Ed (1987) Analysis of Spread Mooring | high | high | digitalmodel | - |
| WRK-TEST-ENSEMBLE | Smoke test for ensemble planning | low | simple | workspace-hub | - |

### Working

| ID | Title | Priority | Complexity | Repos | Module |
|-----|-------|----------|------------|-------|--------|
| WRK-020 | GIS skill for cross-application geospatial tools — Blender, QGIS, well plotting | medium | complex | digitalmodel | - |
| WRK-021 | Stock analysis for drastic trend changes, technical indicators, and insider trading benchmarks | medium | complex | assethold | - |
| WRK-118 | AI agent utilization strategy — leverage Claude, Codex, Gemini for planning, development, testing workflows | medium | complex | workspace-hub | - |
| WRK-121 | Extract & Catalog OrcaFlex Models from rock-oil-field/s7 | high | medium | workspace-hub | - |
| WRK-125 | OrcaFlex module roadmap — evolving coordination and progress tracking | high | low | digitalmodel | - |
| WRK-131 | Passing ship analysis for moored vessels — AQWA-based force calculation and mooring response | high | complex | digitalmodel | - |
| WRK-149 | digitalmodel test coverage improvement (re-creates WRK-051) | high | complex | digitalmodel | - |
| WRK-235 | ROADMAP: Repo ecosystem 3-6 month horizon — plan and gear for agentic AI maturation | high | complex | workspace-hub | - |
| WRK-352 | Set up remote desktop access on ace-linux-2 | low | simple | workspace-hub | - |

### Blocked

| ID | Title | Priority | Complexity | Repos | Module |
|-----|-------|----------|------------|-------|--------|
| WRK-006 | Upload videos from iPhone to YouTube | low | simple | achantas-data | - |
| WRK-064 | OrcaFlex format converter: license-required validation and backward-compat wrapper | medium | medium | digitalmodel | - |
| WRK-069 | Acquire USCG MISLE bulk dataset | high | simple | worldenergydata | - |
| WRK-130 | Standardize analysis reporting for each OrcaWave structure type | high | complex | digitalmodel | - |
| WRK-133 | Update OrcaFlex license agreement with addresses and 3rd-party terms | high | medium | aceengineer-admin | - |

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
| WRK-015 | Metocean data extrapolation to target locations using GIS and nearest-source modeling | medium | complex | worldenergydata | - |
| WRK-016 | BSEE completion and intervention activity analysis for insights | medium | complex | worldenergydata | - |
| WRK-017 | Streamline BSEE field data analysis pipeline — wellbore, casing, drilling, completions, interventions | high | complex | worldenergydata | - |
| WRK-018 | Extend BSEE field data pipeline to other regulatory sources (RRC, Norway, Mexico, Brazil) | low | complex | worldenergydata | - |
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
| WRK-076 | Add data collection scheduler/orchestrator for automated refresh pipelines | medium | complex | worldenergydata | - |
| WRK-077 | Validate and wire decline curve modeling into BSEE production workflow | high | medium | worldenergydata | - |
| WRK-078 | Create energy data case study — BSEE field economics with NPV/IRR workflow | medium | medium | aceengineer-website | - |
| WRK-079 | Create marine safety case study — cross-database incident correlation | medium | medium | aceengineer-website | - |
| WRK-082 | Complete LNG terminal data pipeline — from config to working collection | medium | medium | worldenergydata | - |
| WRK-083 | Validate multi-format export (Excel, PDF, Parquet) with real BSEE data | medium | medium | worldenergydata | - |
| WRK-084 | Integrate metocean data sources into unified aggregation interface | medium | complex | worldenergydata | - |
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
| WRK-111 | BSEE field development interactive map and analytics | medium | complex | worldenergydata, aceengineer-website | - |
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
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | high | complex | digitalmodel | - |
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
| WRK-151 | worldenergydata test coverage improvement (re-creates WRK-054) | medium | medium | worldenergydata | - |
| WRK-152 | Marine safety importer validation — verify MAIB/TSB/IMO/EMSA importers against real data | high | medium | worldenergydata | marine_safety |
| WRK-153 | Energy data case study — BSEE field economics with NPV/IRR workflow | medium | medium | aceengineer-website | - |
| WRK-154 | CI workflow rewrite — fix 2 GitHub Actions workflows | high | medium | workspace-hub | - |
| WRK-155 | DNV-ST-F101 submarine pipeline wall thickness — WSD and LRFD methods | high | complex | digitalmodel | structural |
| WRK-157 | Fatigue analysis module enhancement — S-N curve reporting and parametric sweeps | high | complex | digitalmodel | fatigue |
| WRK-158 | Wall thickness parametric engine — Cartesian sweep across D/t, pressure, material | medium | medium | digitalmodel | structural |
| WRK-159 | Three-way design code comparison report — API RP 1111 vs RP 2RD vs STD 2RD | medium | medium | digitalmodel | structural |
| WRK-160 | OSHA severe injury + fatality data completion and severity mapping fix | medium | simple | worldenergydata | hse |
| WRK-161 | BSEE Excel statistics re-download and URL importer verification | medium | simple | worldenergydata | hse |
| WRK-163 | Well planning risk empowerment framework | medium | complex | worldenergydata, digitalmodel | risk_assessment |
| WRK-164 | Well production test data quality and nodal analysis foundation | high | complex | worldenergydata, digitalmodel | production_engineering |
| WRK-167 | Calendar: Krishna ADHD evaluation — 24 Feb 2:30 PM | high | simple | - | - |
| WRK-168 | MPD systems knowledge module — pressure management for drillships | high | complex | worldenergydata, digitalmodel | drilling_pressure_management |
| WRK-170 | Integrate MET-OM/metocean-stats as statistical analysis engine for metocean module | medium | complex | worldenergydata, digitalmodel | metocean |
| WRK-172 | AI agent usage tracking — real-time quota display, OAuth API, session hooks | high | medium | workspace-hub | ai-tools |
| WRK-177 | Stop Hook: Engineering Calculation Audit Trail | high | medium | workspace-hub, worldenergydata | - |
| WRK-178 | Stop Hook: Data Provenance Snapshot | medium | medium | workspace-hub, worldenergydata | - |
| WRK-179 | Start Hook: Agent Capacity Pre-flight | medium | low | workspace-hub | - |
| WRK-184 | Improve /improve — Bug fixes, recommendations output, startup readiness | high | medium | workspace-hub | - |
| WRK-185 | Ecosystem Truth Review: instruction/skills/work-item centralization | high | medium | workspace-hub, digitalmodel, worldenergydata | governance |
| WRK-186 | Context budget: trim rules/ to under 16KB | high | simple | workspace-hub | - |
| WRK-187 | Improve /improve: usage-based skill health, classify retry, apply API content | medium | medium | workspace-hub | - |
| WRK-188 | Wave-1 spec migration: worldenergydata dry-run manifest and apply plan | high | medium | workspace-hub, worldenergydata | governance |
| WRK-190 | NCS production data module — NPD/Sodir open data integration (worldenergydata) | medium | moderate | worldenergydata | ncs |
| WRK-193 | UKCS production data module — NSTA/OPRED open data integration (worldenergydata) | low | moderate | worldenergydata | ukcs |
| WRK-194 | Brazil ANP production data module — well-level monthly CSV integration (worldenergydata) | high | moderate | worldenergydata | brazil_anp |
| WRK-195 | EIA US production data module — non-GoM onshore + Alaska integration (worldenergydata) | medium | moderate | worldenergydata | eia_us |
| WRK-196 | Canada offshore + emerging basin watch list (C-NLOER NL data; Guyana/Suriname/Namibia/Falklands monitor) | low | moderate | worldenergydata, digitalmodel | canada_offshore + emerging_basins |
| WRK-200 | Filesystem naming cleanup — eliminate duplicate/conflicting dirs across workspace-hub, digitalmodel, worldenergydata | high | complex | - | - |
| WRK-201 | Work queue workflow gate enforcement — plan_reviewed, Route C spec, pre-move checks | high | medium | workspace-hub | work-queue |
| WRK-204 | digitalmodel: rename modules/ naming pattern across docs/, examples/, scripts/python/, base_configs/, tests/ | medium | complex | - | - |
| WRK-205 | Skills knowledge graph — capability metadata and relationship layer beyond flat index | medium | medium | workspace-hub | - |
| WRK-206 | Asset integrity / fitness-for-service (FFS) engineering skill — corrosion damage assessment and run-repair-replace decisions | medium | medium | workspace-hub, digitalmodel | - |
| WRK-207 | Skill relationship maintenance — bidirectional linking as enforced process | medium | small | workspace-hub | - |
| WRK-207 | Wire model-tier routing into work queue plan.sh and execute.sh — Sonnet 4.6 default, Opus 4.6 for Route C plan only | medium | simple | workspace-hub | - |
| WRK-208 | Cross-platform encoding guard — pre-commit + post-pull encoding validation | high | simple | workspace-hub | - |
| WRK-209 | uv enforcement across workspace — eliminate python3/python fallback chains | medium | medium | workspace-hub | - |
| WRK-210 | Interoperability skill — cross-OS standards and health checks for workspace-hub | medium | small | workspace-hub | - |
| WRK-211 | Ecosystem health check skill — parallel agent for session and repo-sync workflows | medium | medium | workspace-hub | - |
| WRK-212 | Agent teams protocol skill — orchestrator routing, subagent patterns, team lifecycle | medium | medium | workspace-hub | - |
| WRK-213 | Codex multi-agent roles — assess native role system vs workspace-hub agent skill approach | medium | medium | workspace-hub | - |
| WRK-214 | Session lifecycle compliance — interview-driven review of all workflow scaffolding | high | medium | workspace-hub | - |
| WRK-215 | Graph-aware skill discovery and enhancement — extend /improve with proactive gap analysis | medium | simple | workspace-hub | - |
| WRK-216 | Subagent learning capture — emit signals to pending-reviews before task completion | medium | simple | workspace-hub | - |
| WRK-217 | Update ecosystem-health-check.sh — remove stale skill count threshold | medium | simple | workspace-hub | - |
| WRK-218 | Well bore design analysis — slim-hole vs. standard-hole hydraulic and mechanical trade-offs | medium | complex | digitalmodel, worldenergydata | well_design |
| WRK-220 | Offshore decommissioning analytics — data-driven lifecycle planning module | medium | complex | worldenergydata, digitalmodel, aceengineer-website | decommissioning_analytics |
| WRK-222 | Pre-clear session snapshot — /save skill + save-snapshot.sh script | medium | low | workspace-hub | - |
| WRK-223 | Workstations registry — hardware inventory, hardware-info.sh, ace-linux-1 specs | medium | low | workspace-hub | - |
| WRK-224 | Tool-readiness SKILL.md — session-start check for CLI, data sources, statusline, work queue | medium | low | workspace-hub | - |
| WRK-225 | Investigate plugins vs skills trade-off for repo ecosystem | medium | medium | workspace-hub | - |
| WRK-226 | Audit and improve agent performance files across Claude, Codex, and Gemini | high | medium | workspace-hub | - |
| WRK-228 | Orient all work items toward agentic AI future-boosting, not just task completion | high | medium | workspace-hub | - |
| WRK-229 | Skills curation — online research, knowledge graph review, update index, session-input health check | high | medium | workspace-hub | - |
| WRK-230 | Holistic session lifecycle — unify gap surfacing, stop hooks, and skill input pipeline | high | medium | workspace-hub | - |
| WRK-231 | session-analysis skill — first-class session mining as foundation for skills, gaps, and agent improvement | high | medium | workspace-hub | - |
| WRK-232 | session-bootstrap skill — one-time historical session analysis per machine | high | simple | workspace-hub | - |
| WRK-233 | Assess and simplify existing workflows in light of session-analysis self-learning loop | high | medium | workspace-hub | - |
| WRK-239 | BSEE field pipeline skill — zero-config agent-callable wrapper | high | medium | worldenergydata | - |
| WRK-240 | Diffraction spec converter skill — register as named agent-callable skill | high | simple | digitalmodel | - |
| WRK-241 | Pipeline integrity skill — chain wall thickness, parametric engine, and FFS into one callable workflow | high | medium | digitalmodel | - |
| WRK-242 | Multi-format export as automatic pipeline output stage | high | medium | worldenergydata, digitalmodel | - |
| WRK-243 | Hull analysis setup skill — chain select, scale, mesh, RAO-link into one call | high | medium | digitalmodel | - |
| WRK-244 | OrcaFlex template library skill — get canonical spec.yml by structure type | high | simple | digitalmodel | - |
| WRK-245 | Fatigue assessment skill — wrap full module with input schema and auto export | high | medium | digitalmodel | - |
| WRK-246 | LNG terminal dataset — queryable module and aceengineer website data card | medium | medium | worldenergydata, aceengineer-website | - |
| WRK-247 | digitalmodel capability manifest — machine-readable module index for agent discovery | medium | simple | digitalmodel | - |
| WRK-248 | PHMSA pipeline safety case study — aceengineer website with data-to-assessment workflow | medium | medium | aceengineer-website, worldenergydata | - |
| WRK-249 | ENIGMA safety analysis skill — register as agent-callable capability | medium | medium | worldenergydata | - |
| WRK-250 | Cross-database marine safety case study — MAIB, IMO, EMSA, TSB correlation analysis | medium | medium | worldenergydata, aceengineer-website | - |
| WRK-252 | worldenergydata module discoverability review — regenerate after new data source modules | medium | simple | worldenergydata | - |
| WRK-255 | Hull library lookup skill — closest-match hull form by target dimensions | medium | simple | digitalmodel | - |
| WRK-258 | Close WRK-153 as superseded — defer BSEE case study rebuild to after WRK-019 and WRK-171 | low | simple | worldenergydata | - |
| WRK-259 | common.units — global unit conversion registry for cross-basin analysis | high | medium | worldenergydata | common.units |
| WRK-260 | Cross-regional production data query interface — unified layer across all 8 basins | high | moderate | worldenergydata | production.unified |
| WRK-265 | Wire CrossDatabaseAnalyzer to live MAIB/IMO/EMSA/TSB importers | high | medium | worldenergydata | marine_safety |
| WRK-266 | Calibrate decommissioning cost model against BSEE platform removal notices | medium | medium | worldenergydata | decommissioning |
| WRK-267 | Calibrate well planning risk probabilities against BSEE incident and HSE data | medium | medium | worldenergydata | well_planning |
| WRK-268 | Wire ENIGMA safety skill to real HSE incident database for data-driven scoring | medium | medium | worldenergydata | safety_analysis |
| WRK-269 | CP standards research — inventory codes, map version gaps, define implementation scope | high | medium | digitalmodel | - |
| WRK-270 | Fix cathodic-protection SKILL.md — align examples to real CathodicProtection API | medium | simple | workspace-hub | - |
| WRK-271 | CP worked examples — end-to-end reference calculations for pipeline, ship, and offshore platform | medium | medium | digitalmodel | - |
| WRK-272 | CP capability extension — DNV-RP-B401 offshore platform + DNV-RP-F103 2016 update | medium | complex | digitalmodel | - |
| WRK-274 | saipem repo content index — searchable catalog of disciplines, project files, and key docs | medium | simple | saipem | - |
| WRK-275 | acma-projects repo content index — catalog projects, codes & standards, and key reference docs | medium | simple | acma-projects | - |
| WRK-276 | Abstract all CP client calcs to .md reference — strip project names, keep engineering data, use as tests | high | medium | digitalmodel, saipem, acma-projects | - |
| WRK-277 | CP capability — ABS GN Offshore Structures 2018 route for ABS-classed offshore structures | medium | complex | digitalmodel | - |
| WRK-278 | Wire legal-sanity-scan into pre-commit for CP-stream repos — activate deny list CI gate | high | simple | digitalmodel, saipem, acma-projects | - |
| WRK-279 | Fix DNV_RP_F103_2010 critical defects G-1 through G-4 — replace fabricated table refs + non-standard formulas | critical | medium | digitalmodel | - |
| WRK-280 | ABS standards acquisition: create folder + download CP Guidance Notes | high | simple | workspace-hub | - |
| WRK-282 | Migrate raw ABS docs from O&G-Standards/raw/ into structured ABS/ folder | high | simple | workspace-hub | - |
| WRK-283 | Navigation layer for 0_mrv/, Production/, umbilical/ legacy roots | medium | simple | workspace-hub | - |
| WRK-285 | Write active WRK id to state file on working/ transition | high | simple | workspace-hub | - |
| WRK-287 | Set up Linux-to-Linux network file sharing for workspace-hub access from ace-linux-2 | medium | medium | workspace-hub | - |
| WRK-290 | Install core engineering suite on ace-linux-2 (Blender, OpenFOAM, FreeCAD, Gmsh, BemRosetta) | medium | medium | workspace-hub | - |
| WRK-299 | comprehensive-learning skill — single batch command for all session learning + ecosystem improvement | high | medium | - | - |
| WRK-300 | workstations skill — evolve from registry to multi-machine work distribution | medium | medium | - | - |
| WRK-303 | Ensemble planning — 3×Claude + 3×Codex + 3×Gemini independent agents for non-deterministic plan diversity | medium | medium | workspace-hub | - |
| WRK-307 | Fix KVM display loss on ace-linux-2 after switching — EDID emulator or config fix | medium | simple | workspace-hub | - |
| WRK-309 | chore: portable Python invocation — consistent cross-machine execution, zero error noise | high | medium | workspace-hub | - |
| WRK-310 | Daily network-mount readiness check — SSHFS mounts always available on both machines | high | low | workspace-hub | - |
| WRK-350 | Fix pre-existing test failures in assetutilities | medium | medium | assetutilities | - |
| WRK-351 | Assign workstation to all pending/working/blocked WRK items + bake into planning workflow | high | medium | workspace-hub | - |
| WRK-357 | Extract offshore vessel fleet data from Offshore Magazine survey PDFs | medium | medium | frontierdeepwater | - |
| WRK-358 | Enrich vessel fleet data with online research — current fleet status + newer surveys | medium | high | frontierdeepwater | - |
| WRK-359 | Design and build vessel marine-parameters database for engineering analysis | medium | high | frontierdeepwater | - |
| WRK-360 | Extract contractor contact data + build offshore contractor BD call list | high | medium | frontierdeepwater, aceengineer-admin | - |
| WRK-364 | Delete Windows-path directory artifacts in digitalmodel and worldenergydata | high | simple | digitalmodel, worldenergydata | - |
| WRK-365 | worldenergydata root cleanup — modules/, validators/, tests/agent_os/ | medium | simple | worldenergydata | - |
| WRK-366 | assethold root cleanup — .agent-os/, business/, agents/, empty dirs | medium | medium | assethold | - |
| WRK-367 | assetutilities src/ cleanup — orphaned src/modules/ and src/validators/ | medium | simple | assetutilities | - |
| WRK-368 | Create repo-structure skill — canonical source layout for all tier-1 repos | medium | simple | workspace-hub | - |
| WRK-369 | Remove agent_os references from digitalmodel .claude/ infrastructure | low | simple | digitalmodel | - |
| WRK-372 | AI-engineering software interface skills — map and build skills AI agents need to drive engineering programs | high | complex | workspace-hub, digitalmodel | - |
| WRK-373 | Vision document — bridge current repo mission to autonomous-production future | medium | complex | workspace-hub | - |
| WRK-374 | Personal habit — get to the point immediately when asking leaders questions | high | simple | - | - |
| WRK-375 | Incorporate SPE Drillbotics mission into ACE Engineering vision and strategy | medium | medium | workspace-hub, digitalmodel | - |
| WRK-377 | ROP prediction model — Bourgoyne-Young and Warren in digitalmodel | high | medium | digitalmodel | - |
| WRK-471 | fix(ace-linux-2): gemini CLI fails on Node 18 with /v regex flag | high | simple | workspace-hub | - |

## By Repository

### OGManufacturing

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-335 | Drilling engineering module — casing design checks per API TR 5C3 | done | medium | high | - |
| WRK-540 | feat(OGManufacturing/structural): Implement API RP 2A — API RP 2A WSD | pending | high | high | - |
| WRK-542 | feat(OGManufacturing/structural): Implement ASTM A131 — ASTM A131 (2004) Std Specification for Structural  | pending | medium | low | - |
| WRK-544 | feat(OGManufacturing/structural): Implement ASTM E1049 — ASTM E1049-85(2005) Standard Practices for Cycle C | pending | high | low | - |
| WRK-546 | feat(OGManufacturing/structural): Implement ASTM E606 — ASTM E606 (2004) Std Practice for Strain-Controlle | pending | medium | low | - |
| WRK-548 | feat(OGManufacturing/structural): Implement ASTM E647 — ASTM E647 (2005) Std Test Method for Measurement o | pending | high | low | - |
| WRK-550 | feat(OGManufacturing/structural): Implement ASTM E466 — ASTM E466 (2002) Std Practice for Conducting Force | pending | medium | low | - |
| WRK-552 | feat(OGManufacturing/structural): Implement ASTM E739 — ASTM E739 (2004) Std Practice for Statistical Anal | pending | medium | low | - |
| WRK-554 | feat(OGManufacturing/structural): Implement ASTM A36 — ASTM A36M-04 (2004) Standard Specification for Car | pending | medium | low | - |

### aceengineer-admin

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-037 | Get OrcaFlex framework of agreement and terms | archived | medium | simple | - |
| WRK-056 | aceengineer-admin test coverage improvement | archived | medium | medium | - |
| WRK-133 | Update OrcaFlex license agreement with addresses and 3rd-party terms | blocked | high | medium | - |
| WRK-346 | Fix aceengineer-admin to standard src/ layout | done | medium | simple | - |
| WRK-360 | Extract contractor contact data + build offshore contractor BD call list | archived | high | medium | - |

### aceengineer-strategy

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-147 | Set up aceengineer-strategy private repo with business operations framework | done | high | complex | - |
| WRK-148 | ACE-GTM: A&CE Go-to-Market strategy stream | pending | high | complex | - |

### aceengineer-website

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-055 | aceengineer-website test coverage improvement | archived | low | simple | - |
| WRK-073 | Market digitalmodel and worldenergydata capabilities on aceengineer website | archived | high | complex | - |
| WRK-078 | Create energy data case study — BSEE field economics with NPV/IRR workflow | archived | medium | medium | - |
| WRK-079 | Create marine safety case study — cross-database incident correlation | archived | medium | medium | - |
| WRK-080 | Write 4 energy data blog posts for SEO | done | low | complex | - |
| WRK-081 | Build interactive NPV calculator for website lead generation | done | low | complex | - |
| WRK-085 | Create public sample data access page on website | done | low | medium | - |
| WRK-111 | BSEE field development interactive map and analytics | archived | medium | complex | - |
| WRK-146 | Overhaul aceengineer-website: fix positioning, narrative, and social proof | done | high | complex | - |
| WRK-148 | ACE-GTM: A&CE Go-to-Market strategy stream | pending | high | complex | - |
| WRK-153 | Energy data case study — BSEE field economics with NPV/IRR workflow | archived | medium | medium | - |
| WRK-169 | Drilling technology evolution — MPD adoption case study | done | medium | medium | content |
| WRK-198 | HSE risk index interactive web dashboard | done | medium | complex | demos/hse-risk-dashboard.html |
| WRK-220 | Offshore decommissioning analytics — data-driven lifecycle planning module | archived | medium | complex | decommissioning_analytics |
| WRK-221 | Offshore resilience design framework — modular platforms, lifecycle planning, structural monitoring | done | low | medium | offshore_resilience |
| WRK-246 | LNG terminal dataset — queryable module and aceengineer website data card | archived | medium | medium | - |
| WRK-248 | PHMSA pipeline safety case study — aceengineer website with data-to-assessment workflow | archived | medium | medium | - |
| WRK-250 | Cross-database marine safety case study — MAIB, IMO, EMSA, TSB correlation analysis | archived | medium | medium | - |
| WRK-259 | BSEE field economics case study — calibrated NPV/IRR with cost data foundation | pending | medium | medium | - |
| WRK-261 | BSEE field economics case study — rebuild on calibrated cost data (WRK-019 + WRK-171) | pending | medium | medium | - |
| WRK-273 | CP marketing brochure — cathodic protection capability document for aceengineer-website | done | low | simple | - |
| WRK-347 | Rename aceengineer-website/src/ to content/ | done | medium | simple | - |
| WRK-382 | Marketing follow-up — update digitalmodel brochure and aceengineer-website for WRK-373/375 outputs | done | low | simple | - |

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
| WRK-141 | Create Achantas family tree to connect all family members | done | medium | medium | - |
| WRK-361 | Heriberto: powder room sink caulk for water drainage | in_progress | medium | simple | - |
| WRK-370 | Heriberto: garage fence door repair | pending | medium | simple | - |
| WRK-371 | Heriberto: powder room faucet tightening | pending | medium | simple | - |

### acma-projects

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-036 | OrcaFlex structure deployment analysis - supply boat side deployment with structural loads | pending | low | complex | - |
| WRK-122 | Licensed Software Usage Workflow & Burden Reduction | archived | high | medium | - |
| WRK-275 | acma-projects repo content index — catalog projects, codes & standards, and key reference docs | archived | medium | simple | - |
| WRK-276 | Abstract all CP client calcs to .md reference — strip project names, keep engineering data, use as tests | archived | high | medium | - |
| WRK-278 | Wire legal-sanity-scan into pre-commit for CP-stream repos — activate deny list CI gate | archived | high | simple | - |
| WRK-338 | LNG tank structural checks — API 620 and EN 14620 thin-shell hoop stress | done | medium | medium | - |
| WRK-339 | Aluminium structural module — Eurocode 9 and AA ADM member capacity checks | done | medium | medium | - |
| WRK-340 | Composite panel design tool — Classical Laminate Theory CLT strength checks | done | medium | high | - |

### assethold

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-021 | Stock analysis for drastic trend changes, technical indicators, and insider trading benchmarks | working | medium | complex | - |
| WRK-022 | US property valuation analysis using GIS — location, traffic, and spatial factors | done | medium | complex | - |
| WRK-023 | Property GIS development timeline with future projection and Google Earth animation | in_progress | low | complex | - |
| WRK-053 | assethold test coverage improvement | archived | medium | medium | - |
| WRK-112 | Appliance lifecycle analytics module for assethold | done | medium | complex | - |
| WRK-253 | Data residence tier compliance audit and extension to assethold | done | medium | medium | - |
| WRK-322 | Fundamentals scoring — P/E P/B EV/EBITDA ranking from yfinance | done | high | medium | - |
| WRK-323 | Covered call analyser — option chain ingestion and premium yield calculator | done | medium | medium | - |
| WRK-324 | Risk metrics — VaR CVaR Sharpe ratio max drawdown per position and portfolio | done | high | medium | - |
| WRK-325 | Sector exposure tracker — auto-classify holdings by GICS sector and flag concentration | done | medium | medium | - |
| WRK-345 | Consolidate validators package into assetutilities | done | high | simple | - |
| WRK-366 | assethold root cleanup — .agent-os/, business/, agents/, empty dirs | archived | medium | medium | - |

### assetutilities

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-052 | assetutilities test coverage improvement | archived | high | complex | - |
| WRK-122 | Licensed Software Usage Workflow & Burden Reduction | archived | high | medium | - |
| WRK-150 | assetutilities test coverage improvement (re-creates WRK-052) | done | medium | medium | - |
| WRK-344 | Remove agent_os from assetutilities | done | high | simple | - |
| WRK-345 | Consolidate validators package into assetutilities | done | high | simple | - |
| WRK-350 | Fix pre-existing test failures in assetutilities | archived | medium | medium | - |
| WRK-367 | assetutilities src/ cleanup — orphaned src/modules/ and src/validators/ | archived | medium | simple | - |
| WRK-383 | Standards-to-Module Capability Map — doc → repo → module linkage | done | high | medium | - |
| WRK-420 | feat(assetutilities/calculations): implement ISO-TR 10400, 1st Ed (2007) Equations... — ISO TR 10400, 1st Ed (2007) Equations and calcu... | done | high | low | - |
| WRK-421 | feat(assetutilities/calculations): implement API BULL 5C3 Formulas and Calculation... — API BULL 5C3 Formulas and Calculations for Casi... | done | high | low | - |
| WRK-422 | feat(assetutilities/calculations): implement 5C — API TR 5C3 (2008) Technical Report on Equations... | done | high | medium | - |
| WRK-423 | feat(assetutilities/calculations): implement API TR 5C3 (2008) Technical Report on... — API TR 5C3 (2008) Technical Report on Equations... | done | high | medium | - |
| WRK-424 | feat(assetutilities/calculations): implement ISO-TR_10400,_1st_Ed_(2007)_Equations... — ISO TR 10400, 1st Ed (2007) Equations and calcu... | done | high | low | - |
| WRK-425 | feat(assetutilities/calculations): implement BS15663 Pt 2 (2001) Life cycle costin... — BS15663 Pt 2 (2001) Life cycle costing   Guidan... | done | high | low | - |
| WRK-426 | feat(assetutilities/calculations): implement Marine Trasportations_0030-4 — Marine Trasportations 0030 4 | done | high | low | - |
| WRK-427 | feat(assetutilities/calculations): implement AMJIG, Rev 2 (2000) Deep Water Drilli... — AMJIG, Rev 2 (2000) Deep Water Drilling Riser I... | done | high | medium | - |
| WRK-428 | feat(assetutilities/calculations): implement AMJIG, Rev2 (1999) Deep Water Drillin... — AMJIG, Rev2 (1999) Deep Water Drilling Riser In... | done | high | medium | - |
| WRK-429 | feat(assetutilities/calculations): implement rpt001-3 Deep Water Drilling Riser In... — rpt001 3 Deep Water Drilling Riser Integ Manag ... | done | high | low | - |
| WRK-430 | feat(assetutilities/calculations): implement AMJIG, Rev1 (1998) Deep Water Drillin... — AMJIG, Rev1 (1998) Deep Water Drilling Riser In... | done | high | medium | - |
| WRK-431 | feat(assetutilities/calculations): implement os-f101[1] — os f101[1] | done | high | low | - |
| WRK-432 | feat(assetutilities/calculations): implement F101 — DNVOS F101 | done | high | low | - |
| WRK-433 | feat(assetutilities/calculations): implement BP - Riser drag dat — BP   Riser drag dat | done | high | low | - |
| WRK-434 | feat(assetutilities/calculations): implement Buoyant Riser_Shear7_Model — Buoyant Riser Shear7 Model | done | high | low | - |
| WRK-435 | feat(assetutilities/calculations): implement TNE011-1 Overestimation of VIV Fatigu... — TNE011 1 Overestimation of VIV Fatigue Damage f... | done | high | low | - |
| WRK-436 | feat(assetutilities/calculations): implement TNE012-1 Internal Pressure Effects on... — TNE012 1 Internal Pressure Effects on Riser Ext... | done | high | low | - |
| WRK-437 | feat(assetutilities/calculations): implement BP Riser Array Design Guidelines v2 — BP Riser Array Design Guidelines v2 | done | high | medium | - |
| WRK-438 | feat(assetutilities/calculations): implement Riser Equivalencing & De-equivalencing — Riser Equivalencing & De equivalencing | done | high | low | - |
| WRK-439 | feat(assetutilities/calculations): implement TNE011-1 Overestimation of VIV Fatigu... — TNE011 1 Overestimation of VIV Fatigue Damage f... | done | high | low | - |
| WRK-440 | feat(assetutilities/calculations): implement Overestimation of VIV Fatigue Damage ... — Overestimation of VIV Fatigue Damage for Single... | done | high | low | - |
| WRK-441 | feat(assetutilities/calculations): implement TNE004-1 Riser Tow Out Analysis Metho... — TNE004 1 Riser Tow Out Analysis Methodology | done | high | low | - |
| WRK-442 | feat(assetutilities/calculations): implement Huse, E., Experimental Investigation ... — Huse, E., Experimental Investigation of Deep Se... | done | high | low | - |
| WRK-443 | feat(assetutilities/calculations): implement Norton, D.J., et al, 1981 - Wind Tunn... — Norton, D.J., et al, 1981   Wind Tunnel Tests o... | done | high | low | - |
| WRK-444 | feat(assetutilities/calculations): implement Vandiver, J.K., et al, 1987 - Hydrody... — Vandiver, J.K., et al, 1987   Hydrodynamic Damp... | done | high | low | - |
| WRK-445 | feat(assetutilities/calculations): implement Smith, C.S., et al, 1981 - Residual S... — Smith, C.S., et al, 1981   Residual Strength an... | done | high | low | - |
| WRK-446 | feat(assetutilities/calculations): implement Javanmardi, K., et al, 1995 - Auger T... — Javanmardi, K., et al, 1995   Auger TLP Well Sy... | done | high | low | - |
| WRK-447 | feat(assetutilities/calculations): implement Fox, S.A., et al, 1995 - Design Analy... — Fox, S.A., et al, 1995   Design Analysis and Fu... | done | high | low | - |
| WRK-448 | feat(assetutilities/calculations): implement Larimore, D., et al, 1998 - Case Hist... — Larimore, D., et al, 1998   Case History   Firs... | done | high | low | - |
| WRK-449 | feat(assetutilities/calculations): implement Allen, D.W., 1995 - Vortex-InducedVib... — Allen, D.W., 1995   Vortex InducedVibration Ana... | done | high | low | - |
| WRK-450 | feat(assetutilities/calculations): implement Brooks, I.H., 1987 - A Pragmatic Appr... — Brooks, I.H., 1987   A Pragmatic Approach to Vo... | done | high | low | - |
| WRK-451 | feat(assetutilities/calculations): implement Carminati, J.R., et al, 1999 - Ursa T... — Carminati, J.R., et al, 1999   Ursa TLP Well Sy... | done | high | low | - |
| WRK-452 | feat(assetutilities/calculations): implement Barton, D.R., et al, 1999 - Genesis P... — Barton, D.R., et al, 1999   Genesis Project   D... | done | high | low | - |
| WRK-453 | feat(assetutilities/calculations): implement OTC1997-8494 Code Conflicts — OTC1997 8494 Code Conflicts | done | high | low | - |
| WRK-454 | feat(assetutilities/calculations): implement OTC2001-13109 SCR Fatigue at Low KC — OTC2001 13109 SCR Fatigue at Low KC | done | high | low | - |
| WRK-455 | feat(assetutilities/calculations): implement Chen, W.C. 1989, Fatigue - Life Predi... — Chen, W.C. 1989, Fatigue   Life Predictions for... | done | high | low | - |
| WRK-456 | feat(assetutilities/calculations): implement Sweeney, T., et al, 1991 - Behaviour ... — Sweeney, T., et al, 1991   Behaviour of 15ksi S... | done | high | low | - |
| WRK-457 | feat(assetutilities/calculations): implement Berner, P., et al, 1997 - Neptune Pro... — Berner, P., et al, 1997   Neptune Project   Pro... | done | high | low | - |
| WRK-458 | feat(assetutilities/calculations): implement Stahl, OTC 3902, Design Methodology f... — Stahl, OTC 3902, Design Methodology for Offshor... | done | high | low | - |
| WRK-459 | feat(assetutilities/calculations): implement Gardner, T.N., et al, 1982 - Deepwate... — Gardner, T.N., et al, 1982   Deepwater Drilling... | done | high | low | - |
| WRK-460 | feat(assetutilities/calculations): implement Allen, D.W., 1998 - Vortex-Induced Vi... — Allen, D.W., 1998   Vortex Induced Vibration of... | done | high | low | - |
| WRK-461 | feat(assetutilities/calculations): implement Kim, Y.Y., et al, 1975 - Analysis of ... — Kim, Y.Y., et al, 1975   Analysis of Simultaneo... | done | high | low | - |
| WRK-462 | feat(assetutilities/calculations): implement Grant, R., 1977 - Riser Fairing for R... — Grant, R., 1977   Riser Fairing for Reduced Dra... | done | high | low | - |
| WRK-463 | feat(assetutilities/calculations): implement Jacobsen, V., et al, 1996 - Vibration... — Jacobsen, V., et al, 1996   Vibration Suppressi... | done | high | low | - |
| WRK-464 | feat(assetutilities/calculations): implement D'Souza, R., et al, 2002 - The Next G... — D'Souza, R., et al, 2002   The Next Generation ... | done | high | low | - |
| WRK-465 | feat(assetutilities/calculations): implement Vandiver, J.K., 1985 - The Prediction... — Vandiver, J.K., 1985   The Prediction of Lockin... | done | high | low | - |
| WRK-466 | feat(assetutilities/calculations): implement Denison, E.B., et al, 1997 - Mars TLP... — Denison, E.B., et al, 1997   Mars TLP Drilling ... | done | high | low | - |
| WRK-467 | feat(assetutilities/calculations): implement Britton, J.S., et al, 1987 - Improvin... — Britton, J.S., et al, 1987   Improving Wellhead... | done | high | low | - |
| WRK-468 | feat(assetutilities/calculations): implement Miller, J.E., et al, 1985 - Influence... — Miller, J.E., et al, 1985   Influence of Mud Co... | done | high | low | - |
| WRK-469 | feat(assetutilities/calculations): implement Imas, L., et al - Sensitivity of SCR ... — Imas, L., et al   Sensitivity of SCR Response a... | done | high | low | - |

### digitalmodel

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-020 | GIS skill for cross-application geospatial tools — Blender, QGIS, well plotting | working | medium | complex | - |
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
| WRK-047 | OpenFOAM CFD analysis capability for digitalmodel | in_progress | low | complex | - |
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
| WRK-099 | Run 3-way benchmark on Unit Box hull | in_progress | medium | medium | - |
| WRK-100 | Run 3-way benchmark on Barge hull | archived | medium | medium | - |
| WRK-101 | Add mesh decimation/coarsening to mesh-utilities skill | done | low | medium | - |
| WRK-106 | Hull panel geometry generator from waterline, section, and profile line definitions | done | medium | complex | - |
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
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | done | high | complex | - |
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | archived | high | complex | - |
| WRK-130 | Standardize analysis reporting for each OrcaWave structure type | blocked | high | complex | - |
| WRK-131 | Passing ship analysis for moored vessels — AQWA-based force calculation and mooring response | working | high | complex | - |
| WRK-132 | Refine OrcaWave benchmarks: barge/ship/spar RAO fixes + damping/gyradii/Km comparison | archived | high | medium | - |
| WRK-138 | Fitness-for-service module enhancement: wall thickness grid, industry targeting, and asset lifecycle | archived | medium | complex | asset_integrity |
| WRK-140 | Integrate gmsh meshing skill into digitalmodel and solver pipelines | pending | medium | medium | - |
| WRK-143 | Full symmetric M-T envelope — closed polygon lens shapes | archived | medium | simple | - |
| WRK-144 | API RP 2RD + API STD 2RD riser wall thickness — WSD & LRFD combined loading | archived | medium | complex | - |
| WRK-145 | Design code versioning — handle changing revisions of standards | archived | medium | medium | - |
| WRK-149 | digitalmodel test coverage improvement (re-creates WRK-051) | working | high | complex | - |
| WRK-155 | DNV-ST-F101 submarine pipeline wall thickness — WSD and LRFD methods | archived | high | complex | structural |
| WRK-156 | FFS Phase 1 — wall thickness grid input with Level 1/2 accept-reject workflow | done | high | complex | asset_integrity |
| WRK-157 | Fatigue analysis module enhancement — S-N curve reporting and parametric sweeps | archived | high | complex | fatigue |
| WRK-158 | Wall thickness parametric engine — Cartesian sweep across D/t, pressure, material | archived | medium | medium | structural |
| WRK-159 | Three-way design code comparison report — API RP 1111 vs RP 2RD vs STD 2RD | archived | medium | medium | structural |
| WRK-163 | Well planning risk empowerment framework | archived | medium | complex | risk_assessment |
| WRK-164 | Well production test data quality and nodal analysis foundation | archived | high | complex | production_engineering |
| WRK-165 | Research subsea intervention analysis opportunities | done | medium | medium | subsea_intervention |
| WRK-168 | MPD systems knowledge module — pressure management for drillships | archived | high | complex | drilling_pressure_management |
| WRK-170 | Integrate MET-OM/metocean-stats as statistical analysis engine for metocean module | archived | medium | complex | metocean |
| WRK-176 | Session Start: Design Code Version Guard | done | high | low | - |
| WRK-183 | Domain Knowledge Graph | done | medium | high | - |
| WRK-185 | Ecosystem Truth Review: instruction/skills/work-item centralization | archived | high | medium | governance |
| WRK-191 | Field development case study catalog — structured reference library of real projects | done | medium | moderate | field_development_references |
| WRK-192 | Field development schematic generator — Python SVG/PNG layout diagrams | done | medium | complex | field_development_visuals |
| WRK-196 | Canada offshore + emerging basin watch list (C-NLOER NL data; Guyana/Suriname/Namibia/Falklands monitor) | archived | low | moderate | canada_offshore + emerging_basins |
| WRK-206 | Asset integrity / fitness-for-service (FFS) engineering skill — corrosion damage assessment and run-repair-replace decisions | archived | medium | medium | - |
| WRK-209 | Add unit validator to EnvironmentSpec.water_density — catch physically implausible values | done | medium | small | - |
| WRK-218 | Well bore design analysis — slim-hole vs. standard-hole hydraulic and mechanical trade-offs | archived | medium | complex | well_design |
| WRK-219 | Batch drilling economics analysis — campaign scheduling and cost optimization | pending | medium | medium | drilling_economics |
| WRK-220 | Offshore decommissioning analytics — data-driven lifecycle planning module | archived | medium | complex | decommissioning_analytics |
| WRK-221 | Offshore resilience design framework — modular platforms, lifecycle planning, structural monitoring | done | low | medium | offshore_resilience |
| WRK-240 | Diffraction spec converter skill — register as named agent-callable skill | archived | high | simple | - |
| WRK-241 | Pipeline integrity skill — chain wall thickness, parametric engine, and FFS into one callable workflow | archived | high | medium | - |
| WRK-242 | Multi-format export as automatic pipeline output stage | archived | high | medium | - |
| WRK-243 | Hull analysis setup skill — chain select, scale, mesh, RAO-link into one call | archived | high | medium | - |
| WRK-244 | OrcaFlex template library skill — get canonical spec.yml by structure type | archived | high | simple | - |
| WRK-245 | Fatigue assessment skill — wrap full module with input schema and auto export | archived | high | medium | - |
| WRK-247 | digitalmodel capability manifest — machine-readable module index for agent discovery | archived | medium | simple | - |
| WRK-251 | Dynacard vision model evaluation — benchmark GPT-4V / Claude Vision vs current heuristics | done | medium | medium | - |
| WRK-253 | Data residence tier compliance audit and extension to assethold | done | medium | medium | - |
| WRK-254 | Heavy vessel GIS integration — connect vessel dataset to GIS skill and BSEE pipeline | done | medium | medium | - |
| WRK-255 | Hull library lookup skill — closest-match hull form by target dimensions | archived | medium | simple | - |
| WRK-256 | Unified parametric study coordinator — orchestrate OrcaFlex, wall thickness, and fatigue sweeps | in-progress | medium | complex | - |
| WRK-269 | CP standards research — inventory codes, map version gaps, define implementation scope | archived | high | medium | - |
| WRK-271 | CP worked examples — end-to-end reference calculations for pipeline, ship, and offshore platform | archived | medium | medium | - |
| WRK-272 | CP capability extension — DNV-RP-B401 offshore platform + DNV-RP-F103 2016 update | archived | medium | complex | - |
| WRK-273 | CP marketing brochure — cathodic protection capability document for aceengineer-website | done | low | simple | - |
| WRK-276 | Abstract all CP client calcs to .md reference — strip project names, keep engineering data, use as tests | archived | high | medium | - |
| WRK-277 | CP capability — ABS GN Offshore Structures 2018 route for ABS-classed offshore structures | archived | medium | complex | - |
| WRK-278 | Wire legal-sanity-scan into pre-commit for CP-stream repos — activate deny list CI gate | archived | high | simple | - |
| WRK-279 | Fix DNV_RP_F103_2010 critical defects G-1 through G-4 — replace fabricated table refs + non-standard formulas | archived | critical | medium | - |
| WRK-310 | explore: OrcFxAPI schematic capture for OrcaWave models (program screenshots) | pending | medium | medium | - |
| WRK-311 | improve: QTF benchmarking for case 3.1 — charts, comparisons, and validation depth | pending | high | medium | - |
| WRK-315 | CALM buoy mooring fatigue — spectral fatigue from OrcaFlex time-domain output | done | medium | high | - |
| WRK-316 | NDBC buoy data ingestion for metocean wave scatter matrices | done | medium | medium | - |
| WRK-327 | Shared engineering constants library — material properties unit conversions seawater properties | done | medium | medium | - |
| WRK-343 | OpenFOAM technical debt and exploration — tutorials, ecosystem audit, WRK-047 refresh | pending | medium | medium | - |
| WRK-353 | Expand S-N curve library from 17 to 20 standards | done | high | medium | - |
| WRK-354 | Structural module — implement jacket and topside analysis | done | high | high | - |
| WRK-355 | Pipeline and flexibles module — pressure containment checks | done | medium | high | - |
| WRK-356 | CP module — sacrificial anode design full calculations per DNV-RP-B401 | done | medium | medium | - |
| WRK-364 | Delete Windows-path directory artifacts in digitalmodel and worldenergydata | archived | high | simple | - |
| WRK-369 | Remove agent_os references from digitalmodel .claude/ infrastructure | archived | low | simple | - |
| WRK-372 | AI-engineering software interface skills — map and build skills AI agents need to drive engineering programs | archived | high | complex | - |
| WRK-375 | Incorporate SPE Drillbotics mission into ACE Engineering vision and strategy | archived | medium | medium | - |
| WRK-376 | Casing/tubing triaxial stress design envelope check (von Mises, API DF, anisotropic grades) | done | medium | medium | - |
| WRK-377 | ROP prediction model — Bourgoyne-Young and Warren in digitalmodel | archived | high | medium | - |
| WRK-378 | Generalise CT hydraulics to full wellbore hydraulics module in digitalmodel | done | high | simple | - |
| WRK-379 | Drilling dysfunction detector — stick-slip, washout, bit balling, kick logic | done | medium | simple | - |
| WRK-380 | Multi-physics simulation chain — Gmsh → OpenFOAM → OrcaFlex as agent-executable pipeline | done | medium | complex | - |
| WRK-382 | Marketing follow-up — update digitalmodel brochure and aceengineer-website for WRK-373/375 outputs | done | low | simple | - |
| WRK-383 | Standards-to-Module Capability Map — doc → repo → module linkage | done | high | medium | - |
| WRK-384 | digitalmodel Module Registry — structured metadata for agent-callable modules | done | high | medium | - |
| WRK-394 | Planing hull motion model — nonlinear 2D+t strip theory for high-speed vessels | done | low | complex | - |
| WRK-417 | The Well — planetswe dataset integration with worldenergydata/metocean | done | medium | medium | - |
| WRK-418 | The Well — acoustic_scattering datasets for subsea NDE validation | done | medium | medium | - |
| WRK-419 | The Well — shear_flow dataset for hydrodynamics ML baseline | done | medium | medium | - |
| WRK-473 | feat(hydrodynamics): integrate wavespectra library for spectral processing | pending | medium | simple | hydrodynamics/wave_spectra |
| WRK-474 | feat(subsea): integrate MoorDyn + MoorPy for mooring analysis | pending | medium | moderate | subsea/mooring_analysis |
| WRK-475 | feat(marine_ops): wire Open-Meteo Marine API into weather-window module | pending | medium | simple | marine_ops/marine_analysis |
| WRK-478 | feat(subsea): create Cathodic Protection module (DNV-RP-B401) | pending | high | moderate | subsea/cp_analysis |
| WRK-481 | feat(digitalmodel): integrate GEBCO_2025 Bathymetry for subsea routing | pending | high | moderate | subsea |
| WRK-482 | feat(digitalmodel/cathodic_protection): Implement API RP 1632 — API RP 1632 Cathodic Protection of Underground Pet | pending | high | high | - |
| WRK-483 | feat(digitalmodel/cathodic_protection): Implement ASTM G80 — ASTM G80 (1998) Std Test Method for Specific Catho | pending | medium | low | - |
| WRK-484 | feat(digitalmodel/cathodic_protection): Implement ASTM G42 — ASTM G42 (1996) Std Test Method for Cathodic Disbo | pending | medium | low | - |
| WRK-485 | feat(digitalmodel/cathodic_protection): Implement ASTM G95 — ASTM G95 (1998) Std Test Method for Cathodic Disbo | pending | medium | low | - |
| WRK-486 | feat(digitalmodel/cathodic_protection): Implement ASTM G8 — ASTM G8 (1996) Std Test Methods for Cathodic Disbo | pending | medium | low | - |
| WRK-487 | feat(digitalmodel/cathodic_protection): Implement ASTM G110 — ASTM G110 (2003) Std Practice for Evaluating Inter | pending | medium | low | - |
| WRK-488 | feat(digitalmodel/cathodic_protection): Implement ISO 15156 — ISO 15156 Pt 3 1st Ed (2003) Cracking-resistant CR | pending | high | medium | - |
| WRK-489 | feat(digitalmodel/cathodic_protection): Implement ISO 11881 — ISO 11881 1st Ed (1999) Corrosion of metals and al | pending | high | medium | - |
| WRK-490 | feat(digitalmodel/cathodic_protection): Implement ISO 11881 — ISO 11881 Corrigendum 1 (1999) Corrosion of metals | pending | high | medium | - |
| WRK-491 | feat(digitalmodel/cathodic_protection): Implement ISO 15589-2 — ISO15589-2-2004forOR Cathodic Protection | pending | high | medium | - |
| WRK-492 | feat(digitalmodel/cathodic_protection): Implement ISO 11846 — ISO 11846 1st Ed (1995) Corrosion of metals and al | pending | high | medium | - |
| WRK-493 | feat(digitalmodel/cathodic_protection): Implement DNV F103 — DNV RP F103 (2010) Cathodic Protection of Submarin | pending | high | medium | - |
| WRK-494 | feat(digitalmodel/cathodic_protection): Implement DNV F106 — DNV RP F106 (2003) Factory Applied External Pipeli | pending | high | medium | - |
| WRK-495 | feat(digitalmodel/cathodic_protection): Implement DNV B401 — DNV RP B401 with 2008 amendments (2005) Cathodic P | pending | high | medium | - |
| WRK-496 | feat(digitalmodel/cathodic_protection): Implement DNV F112 — DNV RP F112 (2008) Stainless steel subsea equipmen | pending | high | medium | - |
| WRK-497 | feat(digitalmodel/pipeline): Implement API RP 1111 — API RP 1111 | pending | high | high | - |
| WRK-499 | feat(digitalmodel/pipeline): Implement API RP 1109 — API RP 1109 Marking Liquid Petroleum Pipeline Faci | pending | high | high | - |
| WRK-501 | feat(digitalmodel/pipeline): Implement ISO 16708 — ISO 16708 1st Ed (2006) Pipeline transportation se | pending | high | medium | - |
| WRK-503 | feat(digitalmodel/pipeline): Implement ISO 13628 — ISO 13628 Pt 7 DRAFT (2003) Completion workover ri | pending | high | medium | - |
| WRK-505 | feat(digitalmodel/pipeline): Implement ISO 13624-1 — DIN EN ISO 13624-1 (2007-11) Risers | pending | high | medium | - |
| WRK-507 | feat(digitalmodel/pipeline): Implement ISO 13628-7 — ISO 13628-7 2005 Completion Workover Risers | pending | high | medium | - |
| WRK-509 | feat(digitalmodel/pipeline): Implement ISO 16389 — ISO 16389 (2003) Dynamic Risers for Floating Produ | pending | high | medium | - |
| WRK-511 | feat(digitalmodel/pipeline): Implement API STD 2RD — API STD 2RD 2nd Ed (2013) Dynamic Risers for Float | pending | high | high | - |
| WRK-513 | feat(digitalmodel/pipeline): Implement DNV F101 — DNV OS F101 (2010) Submarine Pipeline Systems | pending | high | medium | - |
| WRK-515 | feat(digitalmodel/pipeline): Implement API RP 17G — API RP 17G 2nd Ed (2006) Design and Operation of C | pending | high | high | - |
| WRK-517 | feat(digitalmodel/pipeline): Implement DNV OSS 006 — DNV OSS 006 (1981) Rules for Submarine Pipeline Sy | pending | high | medium | - |
| WRK-519 | feat(digitalmodel/pipeline): Implement DNV F201 — DNV OS F201 (2010) Dynamic Risers | pending | high | medium | - |
| WRK-521 | feat(digitalmodel/pipeline): Implement DNV F110 — DNV RP F110 (2007) Global buckling of submarine pi | pending | high | medium | - |
| WRK-523 | feat(digitalmodel/pipeline): Implement DNV F108 — DNV RP F108 with update 2009 (2006) Fracture Contr | pending | high | medium | - |
| WRK-525 | feat(digitalmodel/pipeline): Implement DNV F203 — DNV RP F203 (2009) Riser interference | pending | high | medium | - |
| WRK-527 | feat(digitalmodel/pipeline): Implement DNV F105 — DNV RP F105 (2006) Free Spanning Pipelines | pending | high | medium | - |
| WRK-529 | feat(digitalmodel/pipeline): Implement DNV F102 — DNV RP F102 (2011) Pipeline Field Joint Coating an | pending | high | medium | - |
| WRK-531 | feat(digitalmodel/pipeline): Implement DNV F202 — DNV RP F202 (2010) Composite Risers | pending | high | medium | - |
| WRK-533 | feat(digitalmodel/pipeline): Implement DNV F206 — DNV RP F206 (2008) Riser Integrity Management | pending | high | medium | - |
| WRK-535 | feat(digitalmodel/pipeline): Implement DNV F109 — DNV RP F109 (2007) On-bottom stability design of s | pending | high | medium | - |
| WRK-537 | feat(digitalmodel/pipeline): Implement DNV F116 — DNV RP F116 (2009) Integrity Management of Submari | pending | high | medium | - |
| WRK-539 | feat(digitalmodel/structural): Implement API RP 2A — API RP 2A WSD | pending | high | high | - |
| WRK-541 | feat(digitalmodel/structural): Implement ASTM A131 — ASTM A131 (2004) Std Specification for Structural  | pending | medium | low | - |
| WRK-543 | feat(digitalmodel/structural): Implement ASTM E1049 — ASTM E1049-85(2005) Standard Practices for Cycle C | pending | high | low | - |
| WRK-545 | feat(digitalmodel/structural): Implement ASTM E606 — ASTM E606 (2004) Std Practice for Strain-Controlle | pending | medium | low | - |
| WRK-547 | feat(digitalmodel/structural): Implement ASTM E647 — ASTM E647 (2005) Std Test Method for Measurement o | pending | high | low | - |
| WRK-549 | feat(digitalmodel/structural): Implement ASTM E466 — ASTM E466 (2002) Std Practice for Conducting Force | pending | medium | low | - |
| WRK-551 | feat(digitalmodel/structural): Implement ASTM E739 — ASTM E739 (2004) Std Practice for Statistical Anal | pending | medium | low | - |
| WRK-553 | feat(digitalmodel/structural): Implement ASTM A36 — ASTM A36M-04 (2004) Standard Specification for Car | pending | medium | low | - |
| WRK-555 | feat(digitalmodel/marine): Implement DNV E301 — DNV OS E301 (2010) Position Mooring | pending | high | medium | - |
| WRK-556 | feat(digitalmodel/marine): Implement API RP 2I — API RP 2I 3rd Ed (2008) In-service Inspection of M | pending | high | high | - |
| WRK-557 | feat(digitalmodel/marine): Implement API RP 572 — API RP 572 2nd Ed (2001) Inspection of Pressure Ve | pending | high | high | - |
| WRK-558 | feat(digitalmodel/marine): Implement API RP 2SM — API RP 2SM 1st Ed & Addendum (2001 & 2007) Design, | pending | high | high | - |
| WRK-559 | feat(digitalmodel/marine): Implement API RP 2P — API RP 2P 2nd Ed (1987) Analysis of Spread Mooring | pending | high | high | - |

### doris

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-329 | Formalise doris calculation workflow — migrate ad-hoc calcs to Python modules | done | medium | high | - |
| WRK-330 | DNV-ST-F101 pressure containment checks for subsea pipelines | done | medium | medium | - |
| WRK-331 | API RP 1111 deepwater pipeline design checks — collapse and propagating buckle | done | medium | medium | - |
| WRK-332 | On-bottom stability module — DNV-RP-F109 soil resistance calculations | done | medium | medium | - |
| WRK-498 | feat(doris/pipeline): Implement API RP 1111 — API RP 1111 | pending | high | high | - |
| WRK-500 | feat(doris/pipeline): Implement API RP 1109 — API RP 1109 Marking Liquid Petroleum Pipeline Faci | pending | high | high | - |
| WRK-502 | feat(doris/pipeline): Implement ISO 16708 — ISO 16708 1st Ed (2006) Pipeline transportation se | pending | high | medium | - |
| WRK-504 | feat(doris/pipeline): Implement ISO 13628 — ISO 13628 Pt 7 DRAFT (2003) Completion workover ri | pending | high | medium | - |
| WRK-506 | feat(doris/pipeline): Implement ISO 13624-1 — DIN EN ISO 13624-1 (2007-11) Risers | pending | high | medium | - |
| WRK-508 | feat(doris/pipeline): Implement ISO 13628-7 — ISO 13628-7 2005 Completion Workover Risers | pending | high | medium | - |
| WRK-510 | feat(doris/pipeline): Implement ISO 16389 — ISO 16389 (2003) Dynamic Risers for Floating Produ | pending | high | medium | - |
| WRK-512 | feat(doris/pipeline): Implement API STD 2RD — API STD 2RD 2nd Ed (2013) Dynamic Risers for Float | pending | high | high | - |
| WRK-514 | feat(doris/pipeline): Implement DNV F101 — DNV OS F101 (2010) Submarine Pipeline Systems | pending | high | medium | - |
| WRK-516 | feat(doris/pipeline): Implement API RP 17G — API RP 17G 2nd Ed (2006) Design and Operation of C | pending | high | high | - |
| WRK-518 | feat(doris/pipeline): Implement DNV OSS 006 — DNV OSS 006 (1981) Rules for Submarine Pipeline Sy | pending | high | medium | - |
| WRK-520 | feat(doris/pipeline): Implement DNV F201 — DNV OS F201 (2010) Dynamic Risers | pending | high | medium | - |
| WRK-522 | feat(doris/pipeline): Implement DNV F110 — DNV RP F110 (2007) Global buckling of submarine pi | pending | high | medium | - |
| WRK-524 | feat(doris/pipeline): Implement DNV F108 — DNV RP F108 with update 2009 (2006) Fracture Contr | pending | high | medium | - |
| WRK-526 | feat(doris/pipeline): Implement DNV F203 — DNV RP F203 (2009) Riser interference | pending | high | medium | - |
| WRK-528 | feat(doris/pipeline): Implement DNV F105 — DNV RP F105 (2006) Free Spanning Pipelines | pending | high | medium | - |
| WRK-530 | feat(doris/pipeline): Implement DNV F102 — DNV RP F102 (2011) Pipeline Field Joint Coating an | pending | high | medium | - |
| WRK-532 | feat(doris/pipeline): Implement DNV F202 — DNV RP F202 (2010) Composite Risers | pending | high | medium | - |
| WRK-534 | feat(doris/pipeline): Implement DNV F206 — DNV RP F206 (2008) Riser Integrity Management | pending | high | medium | - |
| WRK-536 | feat(doris/pipeline): Implement DNV F109 — DNV RP F109 (2007) On-bottom stability design of s | pending | high | medium | - |
| WRK-538 | feat(doris/pipeline): Implement DNV F116 — DNV RP F116 (2009) Integrity Management of Submari | pending | high | medium | - |

### frontierdeepwater

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-357 | Extract offshore vessel fleet data from Offshore Magazine survey PDFs | archived | medium | medium | - |
| WRK-358 | Enrich vessel fleet data with online research — current fleet status + newer surveys | archived | medium | high | - |
| WRK-359 | Design and build vessel marine-parameters database for engineering analysis | archived | medium | high | - |
| WRK-360 | Extract contractor contact data + build offshore contractor BD call list | archived | high | medium | - |

### hobbies

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-041 | Develop long-term plan for Hobbies repo | done | low | medium | - |

### investments

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-042 | Develop long-term plan for Investments repo | done | low | medium | - |

### pdf-large-reader

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-341 | Review pdf-large-reader vs native AI agent PDF capabilities — assess continuation or deprecation | done | medium | simple | - |

### rock-oil-field

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-336 | Portable installation analysis library — extract generic OrcaFlex automation from project code | done | medium | high | - |
| WRK-337 | Vessel weather-window calculator — operability analysis from Hs Tp scatter | done | medium | medium | - |

### sabithaandkrishnaestates

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-107 | Clarify Family Dollar 1099-MISC rent amount discrepancy ($50,085.60) | archived | high | simple | - |

### saipem

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-274 | saipem repo content index — searchable catalog of disciplines, project files, and key docs | archived | medium | simple | - |
| WRK-276 | Abstract all CP client calcs to .md reference — strip project names, keep engineering data, use as tests | archived | high | medium | - |
| WRK-278 | Wire legal-sanity-scan into pre-commit for CP-stream repos — activate deny list CI gate | archived | high | simple | - |
| WRK-336 | Portable installation analysis library — extract generic OrcaFlex automation from project code | done | medium | high | - |
| WRK-337 | Vessel weather-window calculator — operability analysis from Hs Tp scatter | done | medium | medium | - |

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
| WRK-118 | AI agent utilization strategy — leverage Claude, Codex, Gemini for planning, development, testing workflows | working | medium | complex | - |
| WRK-119 | Test suite optimization — tiered test profiles for commit, task, and session workflows | archived | high | complex | - |
| WRK-121 | Extract & Catalog OrcaFlex Models from rock-oil-field/s7 | working | high | medium | - |
| WRK-134 | Add future-work brainstorming step before archiving completed items | archived | medium | medium | - |
| WRK-139 | Develop gmsh skill and documentation | archived | medium | medium | - |
| WRK-139 | Unified multi-agent orchestration architecture (Claude/Codex/Gemini) | archived | high | complex | agents |
| WRK-140 | Integrate gmsh meshing skill into digitalmodel and solver pipelines | pending | medium | medium | - |
| WRK-142 | Review work accomplishments and draft Anthropic outreach message | archived | high | medium | - |
| WRK-148 | ACE-GTM: A&CE Go-to-Market strategy stream | pending | high | complex | - |
| WRK-154 | CI workflow rewrite — fix 2 GitHub Actions workflows | archived | high | medium | - |
| WRK-172 | AI agent usage tracking — real-time quota display, OAuth API, session hooks | archived | high | medium | ai-tools |
| WRK-173 | Session Management Workflow Documentation + Schematic | done | high | low | - |
| WRK-175 | Session Start: Engineering Context Loader | done | medium | medium | - |
| WRK-176 | Session Start: Design Code Version Guard | done | high | low | - |
| WRK-177 | Stop Hook: Engineering Calculation Audit Trail | archived | high | medium | - |
| WRK-178 | Stop Hook: Data Provenance Snapshot | archived | medium | medium | - |
| WRK-179 | Start Hook: Agent Capacity Pre-flight | archived | medium | low | - |
| WRK-180 | Stop Hook: Cross-Agent Learning Sync | parked | low | high | - |
| WRK-181 | Session Replay & Time Travel | parked | low | high | - |
| WRK-182 | Predictive Session Planning | parked | low | high | - |
| WRK-183 | Domain Knowledge Graph | done | medium | high | - |
| WRK-184 | Improve /improve — Bug fixes, recommendations output, startup readiness | archived | high | medium | - |
| WRK-185 | Ecosystem Truth Review: instruction/skills/work-item centralization | archived | high | medium | governance |
| WRK-186 | Context budget: trim rules/ to under 16KB | archived | high | simple | - |
| WRK-187 | Improve /improve: usage-based skill health, classify retry, apply API content | archived | medium | medium | - |
| WRK-188 | Wave-1 spec migration: worldenergydata dry-run manifest and apply plan | archived | high | medium | governance |
| WRK-199 | AI agent usage optimizer skill — maximize Claude/Codex/Gemini allocation per task | done | medium | medium | ai-tools |
| WRK-201 | Work queue workflow gate enforcement — plan_reviewed, Route C spec, pre-move checks | archived | high | medium | work-queue |
| WRK-205 | Skills knowledge graph — capability metadata and relationship layer beyond flat index | archived | medium | medium | - |
| WRK-206 | Asset integrity / fitness-for-service (FFS) engineering skill — corrosion damage assessment and run-repair-replace decisions | archived | medium | medium | - |
| WRK-207 | Skill relationship maintenance — bidirectional linking as enforced process | archived | medium | small | - |
| WRK-207 | Wire model-tier routing into work queue plan.sh and execute.sh — Sonnet 4.6 default, Opus 4.6 for Route C plan only | archived | medium | simple | - |
| WRK-208 | Cross-platform encoding guard — pre-commit + post-pull encoding validation | archived | high | simple | - |
| WRK-209 | uv enforcement across workspace — eliminate python3/python fallback chains | archived | medium | medium | - |
| WRK-210 | Interoperability skill — cross-OS standards and health checks for workspace-hub | archived | medium | small | - |
| WRK-211 | Ecosystem health check skill — parallel agent for session and repo-sync workflows | archived | medium | medium | - |
| WRK-212 | Agent teams protocol skill — orchestrator routing, subagent patterns, team lifecycle | archived | medium | medium | - |
| WRK-213 | Codex multi-agent roles — assess native role system vs workspace-hub agent skill approach | archived | medium | medium | - |
| WRK-214 | Session lifecycle compliance — interview-driven review of all workflow scaffolding | archived | high | medium | - |
| WRK-215 | Graph-aware skill discovery and enhancement — extend /improve with proactive gap analysis | archived | medium | simple | - |
| WRK-216 | Subagent learning capture — emit signals to pending-reviews before task completion | archived | medium | simple | - |
| WRK-217 | Update ecosystem-health-check.sh — remove stale skill count threshold | archived | medium | simple | - |
| WRK-222 | Pre-clear session snapshot — /save skill + save-snapshot.sh script | archived | medium | low | - |
| WRK-223 | Workstations registry — hardware inventory, hardware-info.sh, ace-linux-1 specs | archived | medium | low | - |
| WRK-224 | Tool-readiness SKILL.md — session-start check for CLI, data sources, statusline, work queue | done | medium | low | - |
| WRK-224 | Tool-readiness SKILL.md — session-start check for CLI, data sources, statusline, work queue | archived | medium | low | - |
| WRK-225 | Investigate plugins vs skills trade-off for repo ecosystem | archived | medium | medium | - |
| WRK-226 | Audit and improve agent performance files across Claude, Codex, and Gemini | done | high | medium | - |
| WRK-226 | Audit and improve agent performance files across Claude, Codex, and Gemini | archived | high | medium | - |
| WRK-227 | Evaluate cowork relevance — repo ecosystem fit vs agentic coding momentum | parked | medium | medium | - |
| WRK-228 | Orient all work items toward agentic AI future-boosting, not just task completion | archived | high | medium | - |
| WRK-229 | Skills curation — online research, knowledge graph review, update index, session-input health check | done | high | medium | - |
| WRK-229 | Skills curation — online research, knowledge graph review, update index, session-input health check | archived | high | medium | - |
| WRK-230 | Holistic session lifecycle — unify gap surfacing, stop hooks, and skill input pipeline | archived | high | medium | - |
| WRK-231 | session-analysis skill — first-class session mining as foundation for skills, gaps, and agent improvement | archived | high | medium | - |
| WRK-232 | session-bootstrap skill — one-time historical session analysis per machine | archived | high | simple | - |
| WRK-233 | Assess and simplify existing workflows in light of session-analysis self-learning loop | archived | high | medium | - |
| WRK-234 | MISSION: Self-improving agent ecosystem — sessions drive skills, skills drive better sessions | pending | high | complex | - |
| WRK-235 | ROADMAP: Repo ecosystem 3-6 month horizon — plan and gear for agentic AI maturation | working | high | complex | - |
| WRK-236 | Test health trends — track test-writing pairing with code-writing sessions | done | medium | medium | - |
| WRK-237 | Provider cost tracking — token spend per session and per WRK item | done | medium | medium | - |
| WRK-238 | Adopt Codex 0.102.0 TOML role definitions — implement native multi-agent roles in .codex/ | done | medium | medium | - |
| WRK-257 | Agent coordination model ADR — document architectural decision record | done | low | simple | - |
| WRK-262 | Add path-handling guidance to session preflight hook | done | low | simple | - |
| WRK-263 | Progressively reduce agent harness files to ~20 lines by migrating content to skills | done | high | medium | - |
| WRK-264 | Ensure full work-queue workflow parity between Claude and Codex CLI | done | low | medium | - |
| WRK-270 | Fix cathodic-protection SKILL.md — align examples to real CathodicProtection API | archived | medium | simple | - |
| WRK-279 | Audit & govern the /mnt/ace/ Codex relocation plan | complete | high | medium | - |
| WRK-280 | ABS standards acquisition: create folder + download CP Guidance Notes | done | high | simple | - |
| WRK-280 | ABS standards acquisition: create folder + download CP Guidance Notes | archived | high | simple | - |
| WRK-281 | Fix 2H legacy project discoverability (navigation layer) | done | medium | simple | - |
| WRK-282 | Migrate raw ABS docs from O&G-Standards/raw/ into structured ABS/ folder | archived | high | simple | - |
| WRK-283 | Navigation layer for 0_mrv/, Production/, umbilical/ legacy roots | archived | medium | simple | - |
| WRK-285 | Write active WRK id to state file on working/ transition | archived | high | simple | - |
| WRK-286 | Harden chore: commits — require WRK ref for multi-file changes | done | medium | simple | - |
| WRK-287 | Set up Linux-to-Linux network file sharing for workspace-hub access from ace-linux-2 | archived | medium | medium | - |
| WRK-288 | Finish ace-linux-2 setup — install open source engineering programs and map capabilities | done | low | simple | - |
| WRK-289 | Research open source FEA programs for engineering assignments | done | low | medium | - |
| WRK-290 | Install core engineering suite on ace-linux-2 (Blender, OpenFOAM, FreeCAD, Gmsh, BemRosetta) | done | medium | medium | - |
| WRK-290 | Install core engineering suite on ace-linux-2 (Blender, OpenFOAM, FreeCAD, Gmsh, BemRosetta) | archived | medium | medium | - |
| WRK-291 | Install recommended FEA programs on ace-linux-2 | done | low | medium | - |
| WRK-292 | Create capability map — file formats, workflow pipelines, interoperability matrix | done | low | medium | - |
| WRK-293 | SMART health check on ace-linux-2 drives — install smartmontools + run diagnostics | done | high | simple | - |
| WRK-294 | Standardize ace-linux-2 mount paths — fstab entries for HDDs with clean paths | in-progress | high | simple | - |
| WRK-295 | Bidirectional SSH key auth between ace-linux-1 and ace-linux-2 | done | high | simple | - |
| WRK-296 | Install Tailscale VPN on ace-linux-2 — match ace-linux-1 remote access | done | medium | simple | - |
| WRK-297 | SSHFS mounts on ace-linux-1 for ace-linux-2 drives — bidirectional file access | pending | high | simple | - |
| WRK-298 | Install smartmontools on ace-linux-1 + SMART health check on all drives | done | high | simple | - |
| WRK-303 | Ensemble planning — 3×Claude + 3×Codex + 3×Gemini independent agents for non-deterministic plan diversity | archived | medium | medium | - |
| WRK-307 | Fix KVM display loss on ace-linux-2 after switching — EDID emulator or config fix | archived | medium | simple | - |
| WRK-309 | chore: portable Python invocation — consistent cross-machine execution, zero error noise | archived | high | medium | - |
| WRK-310 | explore: OrcFxAPI schematic capture for OrcaWave models (program screenshots) | pending | medium | medium | - |
| WRK-310 | Daily network-mount readiness check — SSHFS mounts always available on both machines | archived | high | low | - |
| WRK-326 | Unified CLI — single ace command routing to all repo tools | done | medium | high | - |
| WRK-327 | Shared engineering constants library — material properties unit conversions seawater properties | done | medium | medium | - |
| WRK-328 | Agent-readable specs index — YAML index of all specs consumable by AI agents | done | medium | medium | - |
| WRK-341 | Review pdf-large-reader vs native AI agent PDF capabilities — assess continuation or deprecation | done | medium | simple | - |
| WRK-342 | Multi-machine workflow clarity — SSH helper scripts, hostname in statusline, CLI consistency across ace-linux-1 and ace-linux-2 | done | high | medium | - |
| WRK-343 | OpenFOAM technical debt and exploration — tutorials, ecosystem audit, WRK-047 refresh | pending | medium | medium | - |
| WRK-348 | Add root pyproject.toml to workspace-hub src/ | done | medium | simple | - |
| WRK-349 | Document client/portfolio repos in ecosystem docs | done | low | simple | - |
| WRK-351 | Assign workstation to all pending/working/blocked WRK items + bake into planning workflow | archived | high | medium | - |
| WRK-352 | Set up remote desktop access on ace-linux-2 | working | low | simple | - |
| WRK-368 | Create repo-structure skill — canonical source layout for all tier-1 repos | archived | medium | simple | - |
| WRK-372 | AI-engineering software interface skills — map and build skills AI agents need to drive engineering programs | archived | high | complex | - |
| WRK-373 | Vision document — bridge current repo mission to autonomous-production future | archived | medium | complex | - |
| WRK-375 | Incorporate SPE Drillbotics mission into ACE Engineering vision and strategy | archived | medium | medium | - |
| WRK-380 | Multi-physics simulation chain — Gmsh → OpenFOAM → OrcaFlex as agent-executable pipeline | done | medium | complex | - |
| WRK-381 | Trust architecture document — formalise plan gate governance for agent-executed actions | done | medium | simple | - |
| WRK-383 | Standards-to-Module Capability Map — doc → repo → module linkage | done | high | medium | - |
| WRK-385 | Superintelligent Engineering Agent Architecture — canonical vision and blueprint | done | high | medium | - |
| WRK-386 | Automated Gap-to-WRK Generator — doc → module gaps spawn new work items | done | medium | medium | - |
| WRK-387 | Claude Code session auto-refresh with WRK context persistence | done | high | complex | - |
| WRK-388 | GIS skills — QGIS, Google Earth Engine, Python GIS ecosystem | done | medium | complex | - |
| WRK-393 | Evaluate Polymathic AI — The Well for ecosystem integration | done | medium | medium | - |
| WRK-470 | feat(gtm): oil-and-gas practitioner persona + 1-month GTM plan for workspace-hub ecosystem | pending | high | medium | - |
| WRK-471 | fix(ace-linux-2): gemini CLI fails on Node 18 with /v regex flag | archived | high | simple | - |
| WRK-TEST-ENSEMBLE | Smoke test for ensemble planning | pending | low | simple | - |

### worldenergydata

| ID | Title | Status | Priority | Complexity | Module |
|-----|-------|--------|----------|------------|--------|
| WRK-009 | Reproduce rev30 lower tertiary BSEE field results for repeatability | archived | high | medium | - |
| WRK-010 | Rerun lower tertiary analysis with latest BSEE data and validate | archived | high | medium | - |
| WRK-011 | Run BSEE analysis for all leases with field nicknames and geological era grouping | archived | high | complex | - |
| WRK-012 | Audit HSE public data coverage and identify gaps | archived | high | medium | - |
| WRK-013 | HSE data analysis to identify typical mishaps by activity and subactivity | archived | high | complex | - |
| WRK-014 | HSE risk index — client-facing risk insights with risk scoring | archived | medium | complex | - |
| WRK-015 | Metocean data extrapolation to target locations using GIS and nearest-source modeling | archived | medium | complex | - |
| WRK-016 | BSEE completion and intervention activity analysis for insights | archived | medium | complex | - |
| WRK-017 | Streamline BSEE field data analysis pipeline — wellbore, casing, drilling, completions, interventions | archived | high | complex | - |
| WRK-018 | Extend BSEE field data pipeline to other regulatory sources (RRC, Norway, Mexico, Brazil) | archived | low | complex | - |
| WRK-019 | Establish drilling, completion, and intervention cost data by region and environment | done | low | complex | - |
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
| WRK-076 | Add data collection scheduler/orchestrator for automated refresh pipelines | archived | medium | complex | - |
| WRK-077 | Validate and wire decline curve modeling into BSEE production workflow | archived | high | medium | - |
| WRK-082 | Complete LNG terminal data pipeline — from config to working collection | archived | medium | medium | - |
| WRK-083 | Validate multi-format export (Excel, PDF, Parquet) with real BSEE data | archived | medium | medium | - |
| WRK-084 | Integrate metocean data sources into unified aggregation interface | archived | medium | complex | - |
| WRK-096 | Review and improve worldenergydata module structure for discoverability | archived | high | medium | - |
| WRK-097 | Implement three-tier data residence strategy (worldenergydata ↔ digitalmodel) | archived | high | medium | - |
| WRK-098 | Clean up 7.1GB large data committed to worldenergydata git history | archived | high | high | - |
| WRK-102 | Add generic hull definition/data for all rigs in worldenergydata | archived | medium | medium | - |
| WRK-103 | Add heavy construction/installation vessel data to worldenergydata | archived | medium | medium | - |
| WRK-104 | Expand drilling rig fleet dataset to all offshore and onshore rigs | archived | high | complex | - |
| WRK-105 | Add drilling riser component data to worldenergydata | archived | medium | medium | - |
| WRK-109 | Review, refine, and curate hooks + skills — research best practices from existing workflows | archived | medium | medium | - |
| WRK-111 | BSEE field development interactive map and analytics | archived | medium | complex | - |
| WRK-113 | Maintain always-current data index with freshness tracking and source metadata | archived | high | medium | - |
| WRK-114 | Collect hull panel shapes and sizes for various floating bodies from existing sources | archived | medium | complex | - |
| WRK-119 | Test suite optimization — tiered test profiles for commit, task, and session workflows | archived | high | complex | - |
| WRK-135 | Ingest XLS historical rig fleet data (163 deepwater rigs) | archived | medium | medium | - |
| WRK-137 | Download and parse rig spec PDFs (102 PDFs from 4 operators) | parked | low | complex | - |
| WRK-151 | worldenergydata test coverage improvement (re-creates WRK-054) | archived | medium | medium | - |
| WRK-152 | Marine safety importer validation — verify MAIB/TSB/IMO/EMSA importers against real data | archived | high | medium | marine_safety |
| WRK-160 | OSHA severe injury + fatality data completion and severity mapping fix | archived | medium | simple | hse |
| WRK-161 | BSEE Excel statistics re-download and URL importer verification | archived | medium | simple | hse |
| WRK-163 | Well planning risk empowerment framework | archived | medium | complex | risk_assessment |
| WRK-164 | Well production test data quality and nodal analysis foundation | archived | high | complex | production_engineering |
| WRK-165 | Research subsea intervention analysis opportunities | done | medium | medium | subsea_intervention |
| WRK-168 | MPD systems knowledge module — pressure management for drillships | archived | high | complex | drilling_pressure_management |
| WRK-169 | Drilling technology evolution — MPD adoption case study | done | medium | medium | content |
| WRK-170 | Integrate MET-OM/metocean-stats as statistical analysis engine for metocean module | archived | medium | complex | metocean |
| WRK-171 | Cost data calibration — sanctioned project benchmarking & multivariate cost prediction | pending | medium | complex | cost |
| WRK-177 | Stop Hook: Engineering Calculation Audit Trail | archived | high | medium | - |
| WRK-178 | Stop Hook: Data Provenance Snapshot | archived | medium | medium | - |
| WRK-183 | Domain Knowledge Graph | done | medium | high | - |
| WRK-185 | Ecosystem Truth Review: instruction/skills/work-item centralization | archived | high | medium | governance |
| WRK-188 | Wave-1 spec migration: worldenergydata dry-run manifest and apply plan | archived | high | medium | governance |
| WRK-190 | NCS production data module — NPD/Sodir open data integration (worldenergydata) | archived | medium | moderate | ncs |
| WRK-193 | UKCS production data module — NSTA/OPRED open data integration (worldenergydata) | archived | low | moderate | ukcs |
| WRK-194 | Brazil ANP production data module — well-level monthly CSV integration (worldenergydata) | archived | high | moderate | brazil_anp |
| WRK-195 | EIA US production data module — non-GoM onshore + Alaska integration (worldenergydata) | archived | medium | moderate | eia_us |
| WRK-196 | Canada offshore + emerging basin watch list (C-NLOER NL data; Guyana/Suriname/Namibia/Falklands monitor) | archived | low | moderate | canada_offshore + emerging_basins |
| WRK-197 | Nigeria NUPRC + EITI data framework — West Africa deepwater and multi-country payment data | done | low | moderate | west_africa |
| WRK-218 | Well bore design analysis — slim-hole vs. standard-hole hydraulic and mechanical trade-offs | archived | medium | complex | well_design |
| WRK-219 | Batch drilling economics analysis — campaign scheduling and cost optimization | pending | medium | medium | drilling_economics |
| WRK-220 | Offshore decommissioning analytics — data-driven lifecycle planning module | archived | medium | complex | decommissioning_analytics |
| WRK-239 | BSEE field pipeline skill — zero-config agent-callable wrapper | archived | high | medium | - |
| WRK-242 | Multi-format export as automatic pipeline output stage | archived | high | medium | - |
| WRK-246 | LNG terminal dataset — queryable module and aceengineer website data card | archived | medium | medium | - |
| WRK-248 | PHMSA pipeline safety case study — aceengineer website with data-to-assessment workflow | archived | medium | medium | - |
| WRK-249 | ENIGMA safety analysis skill — register as agent-callable capability | archived | medium | medium | - |
| WRK-250 | Cross-database marine safety case study — MAIB, IMO, EMSA, TSB correlation analysis | archived | medium | medium | - |
| WRK-252 | worldenergydata module discoverability review — regenerate after new data source modules | archived | medium | simple | - |
| WRK-253 | Data residence tier compliance audit and extension to assethold | done | medium | medium | - |
| WRK-254 | Heavy vessel GIS integration — connect vessel dataset to GIS skill and BSEE pipeline | done | medium | medium | - |
| WRK-258 | Close WRK-153 as superseded — defer BSEE case study rebuild to after WRK-019 and WRK-171 | archived | low | simple | - |
| WRK-259 | BSEE field economics case study — calibrated NPV/IRR with cost data foundation | pending | medium | medium | - |
| WRK-259 | common.units — global unit conversion registry for cross-basin analysis | archived | high | medium | common.units |
| WRK-260 | Cross-regional production data query interface — unified layer across all 8 basins | archived | high | moderate | production.unified |
| WRK-265 | Wire CrossDatabaseAnalyzer to live MAIB/IMO/EMSA/TSB importers | archived | high | medium | marine_safety |
| WRK-266 | Calibrate decommissioning cost model against BSEE platform removal notices | archived | medium | medium | decommissioning |
| WRK-267 | Calibrate well planning risk probabilities against BSEE incident and HSE data | archived | medium | medium | well_planning |
| WRK-268 | Wire ENIGMA safety skill to real HSE incident database for data-driven scoring | archived | medium | medium | safety_analysis |
| WRK-316 | NDBC buoy data ingestion for metocean wave scatter matrices | done | medium | medium | - |
| WRK-317 | Integrated web dashboard — Plotly Dash for BSEE and FDAS data | done | medium | high | - |
| WRK-319 | Real-time EIA and IEA feed ingestion — weekly crude and gas production | done | medium | medium | - |
| WRK-320 | MAIB and NTSB incident correlation with USCG MISLE for root-cause taxonomy | done | low | high | - |
| WRK-321 | Field development economics — MIRR NPV with carbon cost sensitivity | done | medium | medium | - |
| WRK-345 | Consolidate validators package into assetutilities | done | high | simple | - |
| WRK-364 | Delete Windows-path directory artifacts in digitalmodel and worldenergydata | archived | high | simple | - |
| WRK-365 | worldenergydata root cleanup — modules/, validators/, tests/agent_os/ | archived | medium | simple | - |
| WRK-383 | Standards-to-Module Capability Map — doc → repo → module linkage | done | high | medium | - |
| WRK-402 | worldenergydata test structure consolidation | done | low | simple | - |
| WRK-417 | The Well — planetswe dataset integration with worldenergydata/metocean | done | medium | medium | - |
| WRK-476 | feat(worldenergydata): create ESG/Carbon Emissions module | pending | high | moderate | esg_carbon |
| WRK-477 | feat(worldenergydata): create Offshore Geohazard Feed module using USGS API | pending | medium | simple | safety_analysis/geohazard |
| WRK-479 | feat(worldenergydata): wire SODIR FactPages OData API | pending | medium | moderate | sodir |
| WRK-480 | feat(worldenergydata): integrate CMEMS Wave Multi-Year Product | pending | medium | moderate | metocean |

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
| WRK-121 | Extract & Catalog OrcaFlex Models from rock-oil-field/s7 | working | medium | workspace-hub | - |
| WRK-122 | Licensed Software Usage Workflow & Burden Reduction | archived | medium | acma-projects, assetutilities | - |
| WRK-125 | OrcaFlex module roadmap — evolving coordination and progress tracking | working | low | digitalmodel | - |
| WRK-126 | Benchmark all example models across time domain and frequency domain with seed equivalence | pending | complex | digitalmodel | - |
| WRK-127 | Sanitize and categorize ideal spec.yml templates for OrcaFlex input across structure types | archived | medium | digitalmodel | - |
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | done | complex | digitalmodel | - |
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | archived | complex | digitalmodel | - |
| WRK-130 | Standardize analysis reporting for each OrcaWave structure type | blocked | complex | digitalmodel | - |
| WRK-131 | Passing ship analysis for moored vessels — AQWA-based force calculation and mooring response | working | complex | digitalmodel | - |
| WRK-132 | Refine OrcaWave benchmarks: barge/ship/spar RAO fixes + damping/gyradii/Km comparison | archived | medium | digitalmodel | - |
| WRK-133 | Update OrcaFlex license agreement with addresses and 3rd-party terms | blocked | medium | aceengineer-admin | - |
| WRK-139 | Unified multi-agent orchestration architecture (Claude/Codex/Gemini) | archived | complex | workspace-hub | agents |
| WRK-142 | Review work accomplishments and draft Anthropic outreach message | archived | medium | workspace-hub | - |
| WRK-146 | Overhaul aceengineer-website: fix positioning, narrative, and social proof | done | complex | aceengineer-website | - |
| WRK-147 | Set up aceengineer-strategy private repo with business operations framework | done | complex | aceengineer-strategy | - |
| WRK-148 | ACE-GTM: A&CE Go-to-Market strategy stream | pending | complex | aceengineer-website, aceengineer-strategy, workspace-hub | - |
| WRK-149 | digitalmodel test coverage improvement (re-creates WRK-051) | working | complex | digitalmodel | - |
| WRK-152 | Marine safety importer validation — verify MAIB/TSB/IMO/EMSA importers against real data | archived | medium | worldenergydata | marine_safety |
| WRK-154 | CI workflow rewrite — fix 2 GitHub Actions workflows | archived | medium | workspace-hub | - |
| WRK-155 | DNV-ST-F101 submarine pipeline wall thickness — WSD and LRFD methods | archived | complex | digitalmodel | structural |
| WRK-156 | FFS Phase 1 — wall thickness grid input with Level 1/2 accept-reject workflow | done | complex | digitalmodel | asset_integrity |
| WRK-157 | Fatigue analysis module enhancement — S-N curve reporting and parametric sweeps | archived | complex | digitalmodel | fatigue |
| WRK-164 | Well production test data quality and nodal analysis foundation | archived | complex | worldenergydata, digitalmodel | production_engineering |
| WRK-167 | Calendar: Krishna ADHD evaluation — 24 Feb 2:30 PM | done | simple | - | - |
| WRK-167 | Calendar: Krishna ADHD evaluation — 24 Feb 2:30 PM | archived | simple | - | - |
| WRK-168 | MPD systems knowledge module — pressure management for drillships | archived | complex | worldenergydata, digitalmodel | drilling_pressure_management |
| WRK-172 | AI agent usage tracking — real-time quota display, OAuth API, session hooks | archived | medium | workspace-hub | ai-tools |
| WRK-173 | Session Management Workflow Documentation + Schematic | done | low | workspace-hub | - |
| WRK-176 | Session Start: Design Code Version Guard | done | low | workspace-hub, digitalmodel | - |
| WRK-177 | Stop Hook: Engineering Calculation Audit Trail | archived | medium | workspace-hub, worldenergydata | - |
| WRK-184 | Improve /improve — Bug fixes, recommendations output, startup readiness | archived | medium | workspace-hub | - |
| WRK-185 | Ecosystem Truth Review: instruction/skills/work-item centralization | archived | medium | workspace-hub, digitalmodel, worldenergydata | governance |
| WRK-186 | Context budget: trim rules/ to under 16KB | archived | simple | workspace-hub | - |
| WRK-188 | Wave-1 spec migration: worldenergydata dry-run manifest and apply plan | archived | medium | workspace-hub, worldenergydata | governance |
| WRK-194 | Brazil ANP production data module — well-level monthly CSV integration (worldenergydata) | archived | moderate | worldenergydata | brazil_anp |
| WRK-200 | Filesystem naming cleanup — eliminate duplicate/conflicting dirs across workspace-hub, digitalmodel, worldenergydata | archived | complex | - | - |
| WRK-201 | Work queue workflow gate enforcement — plan_reviewed, Route C spec, pre-move checks | archived | medium | workspace-hub | work-queue |
| WRK-208 | Cross-platform encoding guard — pre-commit + post-pull encoding validation | archived | simple | workspace-hub | - |
| WRK-214 | Session lifecycle compliance — interview-driven review of all workflow scaffolding | archived | medium | workspace-hub | - |
| WRK-226 | Audit and improve agent performance files across Claude, Codex, and Gemini | done | medium | workspace-hub | - |
| WRK-226 | Audit and improve agent performance files across Claude, Codex, and Gemini | archived | medium | workspace-hub | - |
| WRK-228 | Cross-machine terminal UX consistency — Windows Git Bash vs Linux terminal | done | medium | - | - |
| WRK-228 | Orient all work items toward agentic AI future-boosting, not just task completion | archived | medium | workspace-hub | - |
| WRK-229 | AI agent QA closure — HTML output + SME verification loop per work item | done | medium | - | - |
| WRK-229 | Skills curation — online research, knowledge graph review, update index, session-input health check | done | medium | workspace-hub | - |
| WRK-229 | Skills curation — online research, knowledge graph review, update index, session-input health check | archived | medium | workspace-hub | - |
| WRK-230 | Holistic session lifecycle — unify gap surfacing, stop hooks, and skill input pipeline | archived | medium | workspace-hub | - |
| WRK-231 | session-analysis skill — first-class session mining as foundation for skills, gaps, and agent improvement | archived | medium | workspace-hub | - |
| WRK-232 | session-bootstrap skill — one-time historical session analysis per machine | archived | simple | workspace-hub | - |
| WRK-233 | Assess and simplify existing workflows in light of session-analysis self-learning loop | archived | medium | workspace-hub | - |
| WRK-234 | MISSION: Self-improving agent ecosystem — sessions drive skills, skills drive better sessions | pending | complex | workspace-hub | - |
| WRK-235 | ROADMAP: Repo ecosystem 3-6 month horizon — plan and gear for agentic AI maturation | working | complex | workspace-hub | - |
| WRK-239 | BSEE field pipeline skill — zero-config agent-callable wrapper | archived | medium | worldenergydata | - |
| WRK-240 | Diffraction spec converter skill — register as named agent-callable skill | archived | simple | digitalmodel | - |
| WRK-241 | Pipeline integrity skill — chain wall thickness, parametric engine, and FFS into one callable workflow | archived | medium | digitalmodel | - |
| WRK-242 | Multi-format export as automatic pipeline output stage | archived | medium | worldenergydata, digitalmodel | - |
| WRK-243 | Hull analysis setup skill — chain select, scale, mesh, RAO-link into one call | archived | medium | digitalmodel | - |
| WRK-244 | OrcaFlex template library skill — get canonical spec.yml by structure type | archived | simple | digitalmodel | - |
| WRK-245 | Fatigue assessment skill — wrap full module with input schema and auto export | archived | medium | digitalmodel | - |
| WRK-259 | common.units — global unit conversion registry for cross-basin analysis | archived | medium | worldenergydata | common.units |
| WRK-260 | Cross-regional production data query interface — unified layer across all 8 basins | archived | moderate | worldenergydata | production.unified |
| WRK-263 | Progressively reduce agent harness files to ~20 lines by migrating content to skills | done | medium | workspace-hub | - |
| WRK-265 | Wire CrossDatabaseAnalyzer to live MAIB/IMO/EMSA/TSB importers | archived | medium | worldenergydata | marine_safety |
| WRK-269 | CP standards research — inventory codes, map version gaps, define implementation scope | archived | medium | digitalmodel | - |
| WRK-276 | Abstract all CP client calcs to .md reference — strip project names, keep engineering data, use as tests | archived | medium | digitalmodel, saipem, acma-projects | - |
| WRK-278 | Wire legal-sanity-scan into pre-commit for CP-stream repos — activate deny list CI gate | archived | simple | digitalmodel, saipem, acma-projects | - |
| WRK-279 | Audit & govern the /mnt/ace/ Codex relocation plan | complete | medium | workspace-hub | - |
| WRK-280 | ABS standards acquisition: create folder + download CP Guidance Notes | done | simple | workspace-hub | - |
| WRK-280 | ABS standards acquisition: create folder + download CP Guidance Notes | archived | simple | workspace-hub | - |
| WRK-282 | Migrate raw ABS docs from O&G-Standards/raw/ into structured ABS/ folder | archived | simple | workspace-hub | - |
| WRK-285 | Write active WRK id to state file on working/ transition | archived | simple | workspace-hub | - |
| WRK-293 | SMART health check on ace-linux-2 drives — install smartmontools + run diagnostics | done | simple | workspace-hub | - |
| WRK-294 | Standardize ace-linux-2 mount paths — fstab entries for HDDs with clean paths | in-progress | simple | workspace-hub | - |
| WRK-295 | Bidirectional SSH key auth between ace-linux-1 and ace-linux-2 | done | simple | workspace-hub | - |
| WRK-297 | SSHFS mounts on ace-linux-1 for ace-linux-2 drives — bidirectional file access | pending | simple | workspace-hub | - |
| WRK-298 | Install smartmontools on ace-linux-1 + SMART health check on all drives | done | simple | workspace-hub | - |
| WRK-299 | comprehensive-learning skill — single batch command for all session learning + ecosystem improvement | archived | medium | - | - |
| WRK-304 | cleanup: one lean Stop hook — consume-signals.sh only, all analysis to nightly cron | done | medium | - | - |
| WRK-307 | track: lean-session hook requirement missed — accountability record | done | medium | - | - |
| WRK-308 | perf: move pre-commit skill validation + readiness checks to nightly cron | done | medium | - | - |
| WRK-309 | chore: portable Python invocation — consistent cross-machine execution, zero error noise | archived | medium | workspace-hub | - |
| WRK-310 | Daily network-mount readiness check — SSHFS mounts always available on both machines | archived | low | workspace-hub | - |
| WRK-311 | improve: QTF benchmarking for case 3.1 — charts, comparisons, and validation depth | pending | medium | digitalmodel | - |
| WRK-313 | feat: new-machine setup guide + bootstrap script — statusline, CLI parity, cron jobs | done | medium | - | - |
| WRK-314 | OrcaFlex Reporting Phase 4 — OrcFxAPI Integration | done | medium | - | - |
| WRK-322 | Fundamentals scoring — P/E P/B EV/EBITDA ranking from yfinance | done | medium | assethold | - |
| WRK-324 | Risk metrics — VaR CVaR Sharpe ratio max drawdown per position and portfolio | done | medium | assethold | - |
| WRK-342 | Multi-machine workflow clarity — SSH helper scripts, hostname in statusline, CLI consistency across ace-linux-1 and ace-linux-2 | done | medium | workspace-hub | - |
| WRK-344 | Remove agent_os from assetutilities | done | simple | assetutilities | - |
| WRK-345 | Consolidate validators package into assetutilities | done | simple | assetutilities, worldenergydata, assethold | - |
| WRK-351 | Assign workstation to all pending/working/blocked WRK items + bake into planning workflow | archived | medium | workspace-hub | - |
| WRK-353 | Expand S-N curve library from 17 to 20 standards | done | medium | digitalmodel | - |
| WRK-354 | Structural module — implement jacket and topside analysis | done | high | digitalmodel | - |
| WRK-360 | Extract contractor contact data + build offshore contractor BD call list | archived | medium | frontierdeepwater, aceengineer-admin | - |
| WRK-363 | Audit and deploy cron schedules across all workstations — comprehensive-learning, session-analysis, model-ids, skills-curation | done | medium | - | - |
| WRK-364 | Delete Windows-path directory artifacts in digitalmodel and worldenergydata | archived | simple | digitalmodel, worldenergydata | - |
| WRK-372 | AI-engineering software interface skills — map and build skills AI agents need to drive engineering programs | archived | complex | workspace-hub, digitalmodel | - |
| WRK-374 | Personal habit — get to the point immediately when asking leaders questions | archived | simple | - | - |
| WRK-377 | ROP prediction model — Bourgoyne-Young and Warren in digitalmodel | archived | medium | digitalmodel | - |
| WRK-378 | Generalise CT hydraulics to full wellbore hydraulics module in digitalmodel | done | simple | digitalmodel | - |
| WRK-383 | Standards-to-Module Capability Map — doc → repo → module linkage | done | medium | workspace-hub, digitalmodel, worldenergydata, assetutilities | - |
| WRK-384 | digitalmodel Module Registry — structured metadata for agent-callable modules | done | medium | digitalmodel | - |
| WRK-385 | Superintelligent Engineering Agent Architecture — canonical vision and blueprint | done | medium | workspace-hub | - |
| WRK-387 | Claude Code session auto-refresh with WRK context persistence | done | complex | workspace-hub | - |
| WRK-420 | feat(assetutilities/calculations): implement ISO-TR 10400, 1st Ed (2007) Equations... — ISO TR 10400, 1st Ed (2007) Equations and calcu... | done | low | assetutilities | - |
| WRK-421 | feat(assetutilities/calculations): implement API BULL 5C3 Formulas and Calculation... — API BULL 5C3 Formulas and Calculations for Casi... | done | low | assetutilities | - |
| WRK-422 | feat(assetutilities/calculations): implement 5C — API TR 5C3 (2008) Technical Report on Equations... | done | medium | assetutilities | - |
| WRK-423 | feat(assetutilities/calculations): implement API TR 5C3 (2008) Technical Report on... — API TR 5C3 (2008) Technical Report on Equations... | done | medium | assetutilities | - |
| WRK-424 | feat(assetutilities/calculations): implement ISO-TR_10400,_1st_Ed_(2007)_Equations... — ISO TR 10400, 1st Ed (2007) Equations and calcu... | done | low | assetutilities | - |
| WRK-425 | feat(assetutilities/calculations): implement BS15663 Pt 2 (2001) Life cycle costin... — BS15663 Pt 2 (2001) Life cycle costing   Guidan... | done | low | assetutilities | - |
| WRK-426 | feat(assetutilities/calculations): implement Marine Trasportations_0030-4 — Marine Trasportations 0030 4 | done | low | assetutilities | - |
| WRK-427 | feat(assetutilities/calculations): implement AMJIG, Rev 2 (2000) Deep Water Drilli... — AMJIG, Rev 2 (2000) Deep Water Drilling Riser I... | done | medium | assetutilities | - |
| WRK-428 | feat(assetutilities/calculations): implement AMJIG, Rev2 (1999) Deep Water Drillin... — AMJIG, Rev2 (1999) Deep Water Drilling Riser In... | done | medium | assetutilities | - |
| WRK-429 | feat(assetutilities/calculations): implement rpt001-3 Deep Water Drilling Riser In... — rpt001 3 Deep Water Drilling Riser Integ Manag ... | done | low | assetutilities | - |
| WRK-430 | feat(assetutilities/calculations): implement AMJIG, Rev1 (1998) Deep Water Drillin... — AMJIG, Rev1 (1998) Deep Water Drilling Riser In... | done | medium | assetutilities | - |
| WRK-431 | feat(assetutilities/calculations): implement os-f101[1] — os f101[1] | done | low | assetutilities | - |
| WRK-432 | feat(assetutilities/calculations): implement F101 — DNVOS F101 | done | low | assetutilities | - |
| WRK-433 | feat(assetutilities/calculations): implement BP - Riser drag dat — BP   Riser drag dat | done | low | assetutilities | - |
| WRK-434 | feat(assetutilities/calculations): implement Buoyant Riser_Shear7_Model — Buoyant Riser Shear7 Model | done | low | assetutilities | - |
| WRK-435 | feat(assetutilities/calculations): implement TNE011-1 Overestimation of VIV Fatigu... — TNE011 1 Overestimation of VIV Fatigue Damage f... | done | low | assetutilities | - |
| WRK-436 | feat(assetutilities/calculations): implement TNE012-1 Internal Pressure Effects on... — TNE012 1 Internal Pressure Effects on Riser Ext... | done | low | assetutilities | - |
| WRK-437 | feat(assetutilities/calculations): implement BP Riser Array Design Guidelines v2 — BP Riser Array Design Guidelines v2 | done | medium | assetutilities | - |
| WRK-438 | feat(assetutilities/calculations): implement Riser Equivalencing & De-equivalencing — Riser Equivalencing & De equivalencing | done | low | assetutilities | - |
| WRK-439 | feat(assetutilities/calculations): implement TNE011-1 Overestimation of VIV Fatigu... — TNE011 1 Overestimation of VIV Fatigue Damage f... | done | low | assetutilities | - |
| WRK-440 | feat(assetutilities/calculations): implement Overestimation of VIV Fatigue Damage ... — Overestimation of VIV Fatigue Damage for Single... | done | low | assetutilities | - |
| WRK-441 | feat(assetutilities/calculations): implement TNE004-1 Riser Tow Out Analysis Metho... — TNE004 1 Riser Tow Out Analysis Methodology | done | low | assetutilities | - |
| WRK-442 | feat(assetutilities/calculations): implement Huse, E., Experimental Investigation ... — Huse, E., Experimental Investigation of Deep Se... | done | low | assetutilities | - |
| WRK-443 | feat(assetutilities/calculations): implement Norton, D.J., et al, 1981 - Wind Tunn... — Norton, D.J., et al, 1981   Wind Tunnel Tests o... | done | low | assetutilities | - |
| WRK-444 | feat(assetutilities/calculations): implement Vandiver, J.K., et al, 1987 - Hydrody... — Vandiver, J.K., et al, 1987   Hydrodynamic Damp... | done | low | assetutilities | - |
| WRK-445 | feat(assetutilities/calculations): implement Smith, C.S., et al, 1981 - Residual S... — Smith, C.S., et al, 1981   Residual Strength an... | done | low | assetutilities | - |
| WRK-446 | feat(assetutilities/calculations): implement Javanmardi, K., et al, 1995 - Auger T... — Javanmardi, K., et al, 1995   Auger TLP Well Sy... | done | low | assetutilities | - |
| WRK-447 | feat(assetutilities/calculations): implement Fox, S.A., et al, 1995 - Design Analy... — Fox, S.A., et al, 1995   Design Analysis and Fu... | done | low | assetutilities | - |
| WRK-448 | feat(assetutilities/calculations): implement Larimore, D., et al, 1998 - Case Hist... — Larimore, D., et al, 1998   Case History   Firs... | done | low | assetutilities | - |
| WRK-449 | feat(assetutilities/calculations): implement Allen, D.W., 1995 - Vortex-InducedVib... — Allen, D.W., 1995   Vortex InducedVibration Ana... | done | low | assetutilities | - |
| WRK-450 | feat(assetutilities/calculations): implement Brooks, I.H., 1987 - A Pragmatic Appr... — Brooks, I.H., 1987   A Pragmatic Approach to Vo... | done | low | assetutilities | - |
| WRK-451 | feat(assetutilities/calculations): implement Carminati, J.R., et al, 1999 - Ursa T... — Carminati, J.R., et al, 1999   Ursa TLP Well Sy... | done | low | assetutilities | - |
| WRK-452 | feat(assetutilities/calculations): implement Barton, D.R., et al, 1999 - Genesis P... — Barton, D.R., et al, 1999   Genesis Project   D... | done | low | assetutilities | - |
| WRK-453 | feat(assetutilities/calculations): implement OTC1997-8494 Code Conflicts — OTC1997 8494 Code Conflicts | done | low | assetutilities | - |
| WRK-454 | feat(assetutilities/calculations): implement OTC2001-13109 SCR Fatigue at Low KC — OTC2001 13109 SCR Fatigue at Low KC | done | low | assetutilities | - |
| WRK-455 | feat(assetutilities/calculations): implement Chen, W.C. 1989, Fatigue - Life Predi... — Chen, W.C. 1989, Fatigue   Life Predictions for... | done | low | assetutilities | - |
| WRK-456 | feat(assetutilities/calculations): implement Sweeney, T., et al, 1991 - Behaviour ... — Sweeney, T., et al, 1991   Behaviour of 15ksi S... | done | low | assetutilities | - |
| WRK-457 | feat(assetutilities/calculations): implement Berner, P., et al, 1997 - Neptune Pro... — Berner, P., et al, 1997   Neptune Project   Pro... | done | low | assetutilities | - |
| WRK-458 | feat(assetutilities/calculations): implement Stahl, OTC 3902, Design Methodology f... — Stahl, OTC 3902, Design Methodology for Offshor... | done | low | assetutilities | - |
| WRK-459 | feat(assetutilities/calculations): implement Gardner, T.N., et al, 1982 - Deepwate... — Gardner, T.N., et al, 1982   Deepwater Drilling... | done | low | assetutilities | - |
| WRK-460 | feat(assetutilities/calculations): implement Allen, D.W., 1998 - Vortex-Induced Vi... — Allen, D.W., 1998   Vortex Induced Vibration of... | done | low | assetutilities | - |
| WRK-461 | feat(assetutilities/calculations): implement Kim, Y.Y., et al, 1975 - Analysis of ... — Kim, Y.Y., et al, 1975   Analysis of Simultaneo... | done | low | assetutilities | - |
| WRK-462 | feat(assetutilities/calculations): implement Grant, R., 1977 - Riser Fairing for R... — Grant, R., 1977   Riser Fairing for Reduced Dra... | done | low | assetutilities | - |
| WRK-463 | feat(assetutilities/calculations): implement Jacobsen, V., et al, 1996 - Vibration... — Jacobsen, V., et al, 1996   Vibration Suppressi... | done | low | assetutilities | - |
| WRK-464 | feat(assetutilities/calculations): implement D'Souza, R., et al, 2002 - The Next G... — D'Souza, R., et al, 2002   The Next Generation ... | done | low | assetutilities | - |
| WRK-465 | feat(assetutilities/calculations): implement Vandiver, J.K., 1985 - The Prediction... — Vandiver, J.K., 1985   The Prediction of Lockin... | done | low | assetutilities | - |
| WRK-466 | feat(assetutilities/calculations): implement Denison, E.B., et al, 1997 - Mars TLP... — Denison, E.B., et al, 1997   Mars TLP Drilling ... | done | low | assetutilities | - |
| WRK-467 | feat(assetutilities/calculations): implement Britton, J.S., et al, 1987 - Improvin... — Britton, J.S., et al, 1987   Improving Wellhead... | done | low | assetutilities | - |
| WRK-468 | feat(assetutilities/calculations): implement Miller, J.E., et al, 1985 - Influence... — Miller, J.E., et al, 1985   Influence of Mud Co... | done | low | assetutilities | - |
| WRK-469 | feat(assetutilities/calculations): implement Imas, L., et al - Sensitivity of SCR ... — Imas, L., et al   Sensitivity of SCR Response a... | done | low | assetutilities | - |
| WRK-470 | feat(gtm): oil-and-gas practitioner persona + 1-month GTM plan for workspace-hub ecosystem | pending | medium | workspace-hub | - |
| WRK-471 | fix(ace-linux-2): gemini CLI fails on Node 18 with /v regex flag | archived | simple | workspace-hub | - |
| WRK-476 | feat(worldenergydata): create ESG/Carbon Emissions module | pending | moderate | worldenergydata | esg_carbon |
| WRK-478 | feat(subsea): create Cathodic Protection module (DNV-RP-B401) | pending | moderate | digitalmodel | subsea/cp_analysis |
| WRK-481 | feat(digitalmodel): integrate GEBCO_2025 Bathymetry for subsea routing | pending | moderate | digitalmodel | subsea |
| WRK-482 | feat(digitalmodel/cathodic_protection): Implement API RP 1632 — API RP 1632 Cathodic Protection of Underground Pet | pending | high | digitalmodel | - |
| WRK-488 | feat(digitalmodel/cathodic_protection): Implement ISO 15156 — ISO 15156 Pt 3 1st Ed (2003) Cracking-resistant CR | pending | medium | digitalmodel | - |
| WRK-489 | feat(digitalmodel/cathodic_protection): Implement ISO 11881 — ISO 11881 1st Ed (1999) Corrosion of metals and al | pending | medium | digitalmodel | - |
| WRK-490 | feat(digitalmodel/cathodic_protection): Implement ISO 11881 — ISO 11881 Corrigendum 1 (1999) Corrosion of metals | pending | medium | digitalmodel | - |
| WRK-491 | feat(digitalmodel/cathodic_protection): Implement ISO 15589-2 — ISO15589-2-2004forOR Cathodic Protection | pending | medium | digitalmodel | - |
| WRK-492 | feat(digitalmodel/cathodic_protection): Implement ISO 11846 — ISO 11846 1st Ed (1995) Corrosion of metals and al | pending | medium | digitalmodel | - |
| WRK-493 | feat(digitalmodel/cathodic_protection): Implement DNV F103 — DNV RP F103 (2010) Cathodic Protection of Submarin | pending | medium | digitalmodel | - |
| WRK-494 | feat(digitalmodel/cathodic_protection): Implement DNV F106 — DNV RP F106 (2003) Factory Applied External Pipeli | pending | medium | digitalmodel | - |
| WRK-495 | feat(digitalmodel/cathodic_protection): Implement DNV B401 — DNV RP B401 with 2008 amendments (2005) Cathodic P | pending | medium | digitalmodel | - |
| WRK-496 | feat(digitalmodel/cathodic_protection): Implement DNV F112 — DNV RP F112 (2008) Stainless steel subsea equipmen | pending | medium | digitalmodel | - |
| WRK-497 | feat(digitalmodel/pipeline): Implement API RP 1111 — API RP 1111 | pending | high | digitalmodel | - |
| WRK-498 | feat(doris/pipeline): Implement API RP 1111 — API RP 1111 | pending | high | doris | - |
| WRK-499 | feat(digitalmodel/pipeline): Implement API RP 1109 — API RP 1109 Marking Liquid Petroleum Pipeline Faci | pending | high | digitalmodel | - |
| WRK-500 | feat(doris/pipeline): Implement API RP 1109 — API RP 1109 Marking Liquid Petroleum Pipeline Faci | pending | high | doris | - |
| WRK-501 | feat(digitalmodel/pipeline): Implement ISO 16708 — ISO 16708 1st Ed (2006) Pipeline transportation se | pending | medium | digitalmodel | - |
| WRK-502 | feat(doris/pipeline): Implement ISO 16708 — ISO 16708 1st Ed (2006) Pipeline transportation se | pending | medium | doris | - |
| WRK-503 | feat(digitalmodel/pipeline): Implement ISO 13628 — ISO 13628 Pt 7 DRAFT (2003) Completion workover ri | pending | medium | digitalmodel | - |
| WRK-504 | feat(doris/pipeline): Implement ISO 13628 — ISO 13628 Pt 7 DRAFT (2003) Completion workover ri | pending | medium | doris | - |
| WRK-505 | feat(digitalmodel/pipeline): Implement ISO 13624-1 — DIN EN ISO 13624-1 (2007-11) Risers | pending | medium | digitalmodel | - |
| WRK-506 | feat(doris/pipeline): Implement ISO 13624-1 — DIN EN ISO 13624-1 (2007-11) Risers | pending | medium | doris | - |
| WRK-507 | feat(digitalmodel/pipeline): Implement ISO 13628-7 — ISO 13628-7 2005 Completion Workover Risers | pending | medium | digitalmodel | - |
| WRK-508 | feat(doris/pipeline): Implement ISO 13628-7 — ISO 13628-7 2005 Completion Workover Risers | pending | medium | doris | - |
| WRK-509 | feat(digitalmodel/pipeline): Implement ISO 16389 — ISO 16389 (2003) Dynamic Risers for Floating Produ | pending | medium | digitalmodel | - |
| WRK-510 | feat(doris/pipeline): Implement ISO 16389 — ISO 16389 (2003) Dynamic Risers for Floating Produ | pending | medium | doris | - |
| WRK-511 | feat(digitalmodel/pipeline): Implement API STD 2RD — API STD 2RD 2nd Ed (2013) Dynamic Risers for Float | pending | high | digitalmodel | - |
| WRK-512 | feat(doris/pipeline): Implement API STD 2RD — API STD 2RD 2nd Ed (2013) Dynamic Risers for Float | pending | high | doris | - |
| WRK-513 | feat(digitalmodel/pipeline): Implement DNV F101 — DNV OS F101 (2010) Submarine Pipeline Systems | pending | medium | digitalmodel | - |
| WRK-514 | feat(doris/pipeline): Implement DNV F101 — DNV OS F101 (2010) Submarine Pipeline Systems | pending | medium | doris | - |
| WRK-515 | feat(digitalmodel/pipeline): Implement API RP 17G — API RP 17G 2nd Ed (2006) Design and Operation of C | pending | high | digitalmodel | - |
| WRK-516 | feat(doris/pipeline): Implement API RP 17G — API RP 17G 2nd Ed (2006) Design and Operation of C | pending | high | doris | - |
| WRK-517 | feat(digitalmodel/pipeline): Implement DNV OSS 006 — DNV OSS 006 (1981) Rules for Submarine Pipeline Sy | pending | medium | digitalmodel | - |
| WRK-518 | feat(doris/pipeline): Implement DNV OSS 006 — DNV OSS 006 (1981) Rules for Submarine Pipeline Sy | pending | medium | doris | - |
| WRK-519 | feat(digitalmodel/pipeline): Implement DNV F201 — DNV OS F201 (2010) Dynamic Risers | pending | medium | digitalmodel | - |
| WRK-520 | feat(doris/pipeline): Implement DNV F201 — DNV OS F201 (2010) Dynamic Risers | pending | medium | doris | - |
| WRK-521 | feat(digitalmodel/pipeline): Implement DNV F110 — DNV RP F110 (2007) Global buckling of submarine pi | pending | medium | digitalmodel | - |
| WRK-522 | feat(doris/pipeline): Implement DNV F110 — DNV RP F110 (2007) Global buckling of submarine pi | pending | medium | doris | - |
| WRK-523 | feat(digitalmodel/pipeline): Implement DNV F108 — DNV RP F108 with update 2009 (2006) Fracture Contr | pending | medium | digitalmodel | - |
| WRK-524 | feat(doris/pipeline): Implement DNV F108 — DNV RP F108 with update 2009 (2006) Fracture Contr | pending | medium | doris | - |
| WRK-525 | feat(digitalmodel/pipeline): Implement DNV F203 — DNV RP F203 (2009) Riser interference | pending | medium | digitalmodel | - |
| WRK-526 | feat(doris/pipeline): Implement DNV F203 — DNV RP F203 (2009) Riser interference | pending | medium | doris | - |
| WRK-527 | feat(digitalmodel/pipeline): Implement DNV F105 — DNV RP F105 (2006) Free Spanning Pipelines | pending | medium | digitalmodel | - |
| WRK-528 | feat(doris/pipeline): Implement DNV F105 — DNV RP F105 (2006) Free Spanning Pipelines | pending | medium | doris | - |
| WRK-529 | feat(digitalmodel/pipeline): Implement DNV F102 — DNV RP F102 (2011) Pipeline Field Joint Coating an | pending | medium | digitalmodel | - |
| WRK-530 | feat(doris/pipeline): Implement DNV F102 — DNV RP F102 (2011) Pipeline Field Joint Coating an | pending | medium | doris | - |
| WRK-531 | feat(digitalmodel/pipeline): Implement DNV F202 — DNV RP F202 (2010) Composite Risers | pending | medium | digitalmodel | - |
| WRK-532 | feat(doris/pipeline): Implement DNV F202 — DNV RP F202 (2010) Composite Risers | pending | medium | doris | - |
| WRK-533 | feat(digitalmodel/pipeline): Implement DNV F206 — DNV RP F206 (2008) Riser Integrity Management | pending | medium | digitalmodel | - |
| WRK-534 | feat(doris/pipeline): Implement DNV F206 — DNV RP F206 (2008) Riser Integrity Management | pending | medium | doris | - |
| WRK-535 | feat(digitalmodel/pipeline): Implement DNV F109 — DNV RP F109 (2007) On-bottom stability design of s | pending | medium | digitalmodel | - |
| WRK-536 | feat(doris/pipeline): Implement DNV F109 — DNV RP F109 (2007) On-bottom stability design of s | pending | medium | doris | - |
| WRK-537 | feat(digitalmodel/pipeline): Implement DNV F116 — DNV RP F116 (2009) Integrity Management of Submari | pending | medium | digitalmodel | - |
| WRK-538 | feat(doris/pipeline): Implement DNV F116 — DNV RP F116 (2009) Integrity Management of Submari | pending | medium | doris | - |
| WRK-539 | feat(digitalmodel/structural): Implement API RP 2A — API RP 2A WSD | pending | high | digitalmodel | - |
| WRK-540 | feat(OGManufacturing/structural): Implement API RP 2A — API RP 2A WSD | pending | high | OGManufacturing | - |
| WRK-543 | feat(digitalmodel/structural): Implement ASTM E1049 — ASTM E1049-85(2005) Standard Practices for Cycle C | pending | low | digitalmodel | - |
| WRK-544 | feat(OGManufacturing/structural): Implement ASTM E1049 — ASTM E1049-85(2005) Standard Practices for Cycle C | pending | low | OGManufacturing | - |
| WRK-547 | feat(digitalmodel/structural): Implement ASTM E647 — ASTM E647 (2005) Std Test Method for Measurement o | pending | low | digitalmodel | - |
| WRK-548 | feat(OGManufacturing/structural): Implement ASTM E647 — ASTM E647 (2005) Std Test Method for Measurement o | pending | low | OGManufacturing | - |
| WRK-555 | feat(digitalmodel/marine): Implement DNV E301 — DNV OS E301 (2010) Position Mooring | pending | medium | digitalmodel | - |
| WRK-556 | feat(digitalmodel/marine): Implement API RP 2I — API RP 2I 3rd Ed (2008) In-service Inspection of M | pending | high | digitalmodel | - |
| WRK-557 | feat(digitalmodel/marine): Implement API RP 572 — API RP 572 2nd Ed (2001) Inspection of Pressure Ve | pending | high | digitalmodel | - |
| WRK-558 | feat(digitalmodel/marine): Implement API RP 2SM — API RP 2SM 1st Ed & Addendum (2001 & 2007) Design, | pending | high | digitalmodel | - |
| WRK-559 | feat(digitalmodel/marine): Implement API RP 2P — API RP 2P 2nd Ed (1987) Analysis of Spread Mooring | pending | high | digitalmodel | - |

### Medium

| ID | Title | Status | Complexity | Repos | Module |
|-----|-------|--------|------------|-------|--------|
| WRK-001 | Repair sink faucet in powder room at 11511 Piping Rock | archived | simple | achantas-data | - |
| WRK-002 | Stove repair with factory service at 11511 Piping Rock | archived | simple | achantas-data | - |
| WRK-003 | Garage clean up | archived | simple | achantas-data | - |
| WRK-004 | Reorganize storage in upstairs bathroom at 11511 Piping Rock | archived | simple | achantas-data | - |
| WRK-007 | Upload videos from Doris computer to YouTube | archived | simple | achantas-data | - |
| WRK-014 | HSE risk index — client-facing risk insights with risk scoring | archived | complex | worldenergydata | - |
| WRK-015 | Metocean data extrapolation to target locations using GIS and nearest-source modeling | archived | complex | worldenergydata | - |
| WRK-016 | BSEE completion and intervention activity analysis for insights | archived | complex | worldenergydata | - |
| WRK-020 | GIS skill for cross-application geospatial tools — Blender, QGIS, well plotting | working | complex | digitalmodel | - |
| WRK-021 | Stock analysis for drastic trend changes, technical indicators, and insider trading benchmarks | working | complex | assethold | - |
| WRK-022 | US property valuation analysis using GIS — location, traffic, and spatial factors | done | complex | assethold | - |
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
| WRK-076 | Add data collection scheduler/orchestrator for automated refresh pipelines | archived | complex | worldenergydata | - |
| WRK-078 | Create energy data case study — BSEE field economics with NPV/IRR workflow | archived | medium | aceengineer-website | - |
| WRK-079 | Create marine safety case study — cross-database incident correlation | archived | medium | aceengineer-website | - |
| WRK-082 | Complete LNG terminal data pipeline — from config to working collection | archived | medium | worldenergydata | - |
| WRK-083 | Validate multi-format export (Excel, PDF, Parquet) with real BSEE data | archived | medium | worldenergydata | - |
| WRK-084 | Integrate metocean data sources into unified aggregation interface | archived | complex | worldenergydata | - |
| WRK-086 | Rewrite CI workflows for Python/bash workspace | archived | medium | workspace-hub | - |
| WRK-090 | Identify and refactor large files exceeding 400-line limit | archived | medium | workspace-hub | - |
| WRK-099 | Run 3-way benchmark on Unit Box hull | in_progress | medium | digitalmodel | - |
| WRK-100 | Run 3-way benchmark on Barge hull | archived | medium | digitalmodel | - |
| WRK-102 | Add generic hull definition/data for all rigs in worldenergydata | archived | medium | worldenergydata | - |
| WRK-103 | Add heavy construction/installation vessel data to worldenergydata | archived | medium | worldenergydata | - |
| WRK-105 | Add drilling riser component data to worldenergydata | archived | medium | worldenergydata | - |
| WRK-106 | Hull panel geometry generator from waterline, section, and profile line definitions | done | complex | digitalmodel | - |
| WRK-108 | Agent usage credits display — show remaining quota at session start for weekly planning | archived | medium | workspace-hub | - |
| WRK-109 | Review, refine, and curate hooks + skills — research best practices from existing workflows | archived | medium | workspace-hub, worldenergydata, digitalmodel | - |
| WRK-110 | Expand hull size library with FST, LNGC, and OrcaFlex benchmark shapes | archived | complex | digitalmodel | - |
| WRK-111 | BSEE field development interactive map and analytics | archived | complex | worldenergydata, aceengineer-website | - |
| WRK-112 | Appliance lifecycle analytics module for assethold | done | complex | assethold | - |
| WRK-114 | Collect hull panel shapes and sizes for various floating bodies from existing sources | archived | complex | digitalmodel, worldenergydata | - |
| WRK-115 | Link RAO data to hull shapes in hull library catalog | archived | medium | digitalmodel | - |
| WRK-116 | Scale hull panel meshes to target principal dimensions for hydrodynamic analysis | archived | medium | digitalmodel | - |
| WRK-117 | Refine and coarsen hull panel meshes for mesh convergence sensitivity analysis | archived | complex | digitalmodel | - |
| WRK-118 | AI agent utilization strategy — leverage Claude, Codex, Gemini for planning, development, testing workflows | working | complex | workspace-hub | - |
| WRK-124 | Session 20260211_095832 — 1 file(s) created | archived | low | digitalmodel | - |
| WRK-134 | Add future-work brainstorming step before archiving completed items | archived | medium | workspace-hub | - |
| WRK-135 | Ingest XLS historical rig fleet data (163 deepwater rigs) | archived | medium | worldenergydata | - |
| WRK-138 | Fitness-for-service module enhancement: wall thickness grid, industry targeting, and asset lifecycle | archived | complex | digitalmodel | asset_integrity |
| WRK-139 | Develop gmsh skill and documentation | archived | medium | workspace-hub | - |
| WRK-140 | Integrate gmsh meshing skill into digitalmodel and solver pipelines | pending | medium | digitalmodel, workspace-hub | - |
| WRK-141 | Create Achantas family tree to connect all family members | done | medium | achantas-data | - |
| WRK-143 | Full symmetric M-T envelope — closed polygon lens shapes | archived | simple | digitalmodel | - |
| WRK-144 | API RP 2RD + API STD 2RD riser wall thickness — WSD & LRFD combined loading | archived | complex | digitalmodel | - |
| WRK-145 | Design code versioning — handle changing revisions of standards | archived | medium | digitalmodel | - |
| WRK-150 | assetutilities test coverage improvement (re-creates WRK-052) | done | medium | assetutilities | - |
| WRK-151 | worldenergydata test coverage improvement (re-creates WRK-054) | archived | medium | worldenergydata | - |
| WRK-153 | Energy data case study — BSEE field economics with NPV/IRR workflow | archived | medium | aceengineer-website | - |
| WRK-158 | Wall thickness parametric engine — Cartesian sweep across D/t, pressure, material | archived | medium | digitalmodel | structural |
| WRK-159 | Three-way design code comparison report — API RP 1111 vs RP 2RD vs STD 2RD | archived | medium | digitalmodel | structural |
| WRK-160 | OSHA severe injury + fatality data completion and severity mapping fix | archived | simple | worldenergydata | hse |
| WRK-161 | BSEE Excel statistics re-download and URL importer verification | archived | simple | worldenergydata | hse |
| WRK-163 | Well planning risk empowerment framework | archived | complex | worldenergydata, digitalmodel | risk_assessment |
| WRK-165 | Research subsea intervention analysis opportunities | done | medium | digitalmodel, worldenergydata | subsea_intervention |
| WRK-166 | Jabra USB dongle lost — research universal dongle compatibility | done | simple | - | - |
| WRK-169 | Drilling technology evolution — MPD adoption case study | done | medium | aceengineer-website, worldenergydata | content |
| WRK-170 | Integrate MET-OM/metocean-stats as statistical analysis engine for metocean module | archived | complex | worldenergydata, digitalmodel | metocean |
| WRK-171 | Cost data calibration — sanctioned project benchmarking & multivariate cost prediction | pending | complex | worldenergydata | cost |
| WRK-175 | Session Start: Engineering Context Loader | done | medium | workspace-hub | - |
| WRK-178 | Stop Hook: Data Provenance Snapshot | archived | medium | workspace-hub, worldenergydata | - |
| WRK-179 | Start Hook: Agent Capacity Pre-flight | archived | low | workspace-hub | - |
| WRK-183 | Domain Knowledge Graph | done | high | workspace-hub, worldenergydata, digitalmodel | - |
| WRK-187 | Improve /improve: usage-based skill health, classify retry, apply API content | archived | medium | workspace-hub | - |
| WRK-190 | NCS production data module — NPD/Sodir open data integration (worldenergydata) | archived | moderate | worldenergydata | ncs |
| WRK-191 | Field development case study catalog — structured reference library of real projects | done | moderate | digitalmodel | field_development_references |
| WRK-192 | Field development schematic generator — Python SVG/PNG layout diagrams | done | complex | digitalmodel | field_development_visuals |
| WRK-195 | EIA US production data module — non-GoM onshore + Alaska integration (worldenergydata) | archived | moderate | worldenergydata | eia_us |
| WRK-198 | HSE risk index interactive web dashboard | done | complex | aceengineer-website | demos/hse-risk-dashboard.html |
| WRK-199 | AI agent usage optimizer skill — maximize Claude/Codex/Gemini allocation per task | done | medium | workspace-hub | ai-tools |
| WRK-204 | digitalmodel: rename modules/ naming pattern across docs/, examples/, scripts/python/, base_configs/, tests/ | archived | complex | - | - |
| WRK-205 | Skills knowledge graph — capability metadata and relationship layer beyond flat index | archived | medium | workspace-hub | - |
| WRK-206 | Asset integrity / fitness-for-service (FFS) engineering skill — corrosion damage assessment and run-repair-replace decisions | archived | medium | workspace-hub, digitalmodel | - |
| WRK-207 | Skill relationship maintenance — bidirectional linking as enforced process | archived | small | workspace-hub | - |
| WRK-207 | Wire model-tier routing into work queue plan.sh and execute.sh — Sonnet 4.6 default, Opus 4.6 for Route C plan only | archived | simple | workspace-hub | - |
| WRK-209 | Add unit validator to EnvironmentSpec.water_density — catch physically implausible values | done | small | digitalmodel | - |
| WRK-209 | uv enforcement across workspace — eliminate python3/python fallback chains | archived | medium | workspace-hub | - |
| WRK-210 | Interoperability skill — cross-OS standards and health checks for workspace-hub | archived | small | workspace-hub | - |
| WRK-211 | Ecosystem health check skill — parallel agent for session and repo-sync workflows | archived | medium | workspace-hub | - |
| WRK-212 | Agent teams protocol skill — orchestrator routing, subagent patterns, team lifecycle | archived | medium | workspace-hub | - |
| WRK-213 | Codex multi-agent roles — assess native role system vs workspace-hub agent skill approach | archived | medium | workspace-hub | - |
| WRK-215 | Graph-aware skill discovery and enhancement — extend /improve with proactive gap analysis | archived | simple | workspace-hub | - |
| WRK-216 | Subagent learning capture — emit signals to pending-reviews before task completion | archived | simple | workspace-hub | - |
| WRK-217 | Update ecosystem-health-check.sh — remove stale skill count threshold | archived | simple | workspace-hub | - |
| WRK-218 | Well bore design analysis — slim-hole vs. standard-hole hydraulic and mechanical trade-offs | archived | complex | digitalmodel, worldenergydata | well_design |
| WRK-219 | Batch drilling economics analysis — campaign scheduling and cost optimization | pending | medium | worldenergydata, digitalmodel | drilling_economics |
| WRK-220 | Offshore decommissioning analytics — data-driven lifecycle planning module | archived | complex | worldenergydata, digitalmodel, aceengineer-website | decommissioning_analytics |
| WRK-222 | Pre-clear session snapshot — /save skill + save-snapshot.sh script | archived | low | workspace-hub | - |
| WRK-223 | Workstations registry — hardware inventory, hardware-info.sh, ace-linux-1 specs | archived | low | workspace-hub | - |
| WRK-224 | Tool-readiness SKILL.md — session-start check for CLI, data sources, statusline, work queue | done | low | workspace-hub | - |
| WRK-224 | Tool-readiness SKILL.md — session-start check for CLI, data sources, statusline, work queue | archived | low | workspace-hub | - |
| WRK-225 | Investigate plugins vs skills trade-off for repo ecosystem | archived | medium | workspace-hub | - |
| WRK-227 | Evaluate cowork relevance — repo ecosystem fit vs agentic coding momentum | parked | medium | workspace-hub | - |
| WRK-236 | Test health trends — track test-writing pairing with code-writing sessions | done | medium | workspace-hub | - |
| WRK-237 | Provider cost tracking — token spend per session and per WRK item | done | medium | workspace-hub | - |
| WRK-238 | Adopt Codex 0.102.0 TOML role definitions — implement native multi-agent roles in .codex/ | done | medium | workspace-hub | - |
| WRK-246 | LNG terminal dataset — queryable module and aceengineer website data card | archived | medium | worldenergydata, aceengineer-website | - |
| WRK-247 | digitalmodel capability manifest — machine-readable module index for agent discovery | archived | simple | digitalmodel | - |
| WRK-248 | PHMSA pipeline safety case study — aceengineer website with data-to-assessment workflow | archived | medium | aceengineer-website, worldenergydata | - |
| WRK-249 | ENIGMA safety analysis skill — register as agent-callable capability | archived | medium | worldenergydata | - |
| WRK-250 | Cross-database marine safety case study — MAIB, IMO, EMSA, TSB correlation analysis | archived | medium | worldenergydata, aceengineer-website | - |
| WRK-251 | Dynacard vision model evaluation — benchmark GPT-4V / Claude Vision vs current heuristics | done | medium | digitalmodel | - |
| WRK-252 | worldenergydata module discoverability review — regenerate after new data source modules | archived | simple | worldenergydata | - |
| WRK-253 | Data residence tier compliance audit and extension to assethold | done | medium | worldenergydata, digitalmodel, assethold | - |
| WRK-254 | Heavy vessel GIS integration — connect vessel dataset to GIS skill and BSEE pipeline | done | medium | worldenergydata, digitalmodel | - |
| WRK-255 | Hull library lookup skill — closest-match hull form by target dimensions | archived | simple | digitalmodel | - |
| WRK-256 | Unified parametric study coordinator — orchestrate OrcaFlex, wall thickness, and fatigue sweeps | in-progress | complex | digitalmodel | - |
| WRK-259 | BSEE field economics case study — calibrated NPV/IRR with cost data foundation | pending | medium | aceengineer-website, worldenergydata | - |
| WRK-261 | BSEE field economics case study — rebuild on calibrated cost data (WRK-019 + WRK-171) | pending | medium | aceengineer-website | - |
| WRK-266 | Calibrate decommissioning cost model against BSEE platform removal notices | archived | medium | worldenergydata | decommissioning |
| WRK-267 | Calibrate well planning risk probabilities against BSEE incident and HSE data | archived | medium | worldenergydata | well_planning |
| WRK-268 | Wire ENIGMA safety skill to real HSE incident database for data-driven scoring | archived | medium | worldenergydata | safety_analysis |
| WRK-270 | Fix cathodic-protection SKILL.md — align examples to real CathodicProtection API | archived | simple | workspace-hub | - |
| WRK-271 | CP worked examples — end-to-end reference calculations for pipeline, ship, and offshore platform | archived | medium | digitalmodel | - |
| WRK-272 | CP capability extension — DNV-RP-B401 offshore platform + DNV-RP-F103 2016 update | archived | complex | digitalmodel | - |
| WRK-274 | saipem repo content index — searchable catalog of disciplines, project files, and key docs | archived | simple | saipem | - |
| WRK-275 | acma-projects repo content index — catalog projects, codes & standards, and key reference docs | archived | simple | acma-projects | - |
| WRK-277 | CP capability — ABS GN Offshore Structures 2018 route for ABS-classed offshore structures | archived | complex | digitalmodel | - |
| WRK-281 | Fix 2H legacy project discoverability (navigation layer) | done | simple | workspace-hub | - |
| WRK-283 | Navigation layer for 0_mrv/, Production/, umbilical/ legacy roots | archived | simple | workspace-hub | - |
| WRK-286 | Harden chore: commits — require WRK ref for multi-file changes | done | simple | workspace-hub | - |
| WRK-287 | Set up Linux-to-Linux network file sharing for workspace-hub access from ace-linux-2 | archived | medium | workspace-hub | - |
| WRK-290 | Install core engineering suite on ace-linux-2 (Blender, OpenFOAM, FreeCAD, Gmsh, BemRosetta) | done | medium | workspace-hub | - |
| WRK-290 | Install core engineering suite on ace-linux-2 (Blender, OpenFOAM, FreeCAD, Gmsh, BemRosetta) | archived | medium | workspace-hub | - |
| WRK-296 | Install Tailscale VPN on ace-linux-2 — match ace-linux-1 remote access | done | simple | workspace-hub | - |
| WRK-300 | workstations skill — evolve from registry to multi-machine work distribution | archived | medium | - | - |
| WRK-301 | fix: recurring Write correction pattern — not responding to improve | done | medium | - | - |
| WRK-302 | fix: recurring Edit correction pattern — not responding to improve | done | medium | - | - |
| WRK-303 | Ensemble planning — 3×Claude + 3×Codex + 3×Gemini independent agents for non-deterministic plan diversity | archived | medium | workspace-hub | - |
| WRK-305 | feat: session signal emitters — wire /clear, plan-mode, per-WRK tool-counts | done | medium | - | - |
| WRK-306 | feat: AI agent readiness check — claude/codex/gemini CLI versions + default models | done | medium | - | - |
| WRK-307 | Fix KVM display loss on ace-linux-2 after switching — EDID emulator or config fix | archived | simple | workspace-hub | - |
| WRK-310 | explore: OrcFxAPI schematic capture for OrcaWave models (program screenshots) | pending | medium | digitalmodel, workspace-hub | - |
| WRK-315 | CALM buoy mooring fatigue — spectral fatigue from OrcaFlex time-domain output | done | high | digitalmodel | - |
| WRK-316 | NDBC buoy data ingestion for metocean wave scatter matrices | done | medium | worldenergydata, digitalmodel | - |
| WRK-317 | Integrated web dashboard — Plotly Dash for BSEE and FDAS data | done | high | worldenergydata | - |
| WRK-319 | Real-time EIA and IEA feed ingestion — weekly crude and gas production | done | medium | worldenergydata | - |
| WRK-321 | Field development economics — MIRR NPV with carbon cost sensitivity | done | medium | worldenergydata | - |
| WRK-323 | Covered call analyser — option chain ingestion and premium yield calculator | done | medium | assethold | - |
| WRK-325 | Sector exposure tracker — auto-classify holdings by GICS sector and flag concentration | done | medium | assethold | - |
| WRK-326 | Unified CLI — single ace command routing to all repo tools | done | high | workspace-hub | - |
| WRK-327 | Shared engineering constants library — material properties unit conversions seawater properties | done | medium | workspace-hub, digitalmodel | - |
| WRK-328 | Agent-readable specs index — YAML index of all specs consumable by AI agents | done | medium | workspace-hub | - |
| WRK-329 | Formalise doris calculation workflow — migrate ad-hoc calcs to Python modules | done | high | doris | - |
| WRK-330 | DNV-ST-F101 pressure containment checks for subsea pipelines | done | medium | doris | - |
| WRK-331 | API RP 1111 deepwater pipeline design checks — collapse and propagating buckle | done | medium | doris | - |
| WRK-332 | On-bottom stability module — DNV-RP-F109 soil resistance calculations | done | medium | doris | - |
| WRK-335 | Drilling engineering module — casing design checks per API TR 5C3 | done | high | OGManufacturing | - |
| WRK-336 | Portable installation analysis library — extract generic OrcaFlex automation from project code | done | high | saipem, rock-oil-field | - |
| WRK-337 | Vessel weather-window calculator — operability analysis from Hs Tp scatter | done | medium | saipem, rock-oil-field | - |
| WRK-338 | LNG tank structural checks — API 620 and EN 14620 thin-shell hoop stress | done | medium | acma-projects | - |
| WRK-339 | Aluminium structural module — Eurocode 9 and AA ADM member capacity checks | done | medium | acma-projects | - |
| WRK-340 | Composite panel design tool — Classical Laminate Theory CLT strength checks | done | high | acma-projects | - |
| WRK-341 | Review pdf-large-reader vs native AI agent PDF capabilities — assess continuation or deprecation | done | simple | pdf-large-reader, workspace-hub | - |
| WRK-343 | OpenFOAM technical debt and exploration — tutorials, ecosystem audit, WRK-047 refresh | pending | medium | workspace-hub, digitalmodel | - |
| WRK-346 | Fix aceengineer-admin to standard src/ layout | done | simple | aceengineer-admin | - |
| WRK-347 | Rename aceengineer-website/src/ to content/ | done | simple | aceengineer-website | - |
| WRK-348 | Add root pyproject.toml to workspace-hub src/ | done | simple | workspace-hub | - |
| WRK-350 | Fix pre-existing test failures in assetutilities | archived | medium | assetutilities | - |
| WRK-355 | Pipeline and flexibles module — pressure containment checks | done | high | digitalmodel | - |
| WRK-356 | CP module — sacrificial anode design full calculations per DNV-RP-B401 | done | medium | digitalmodel | - |
| WRK-357 | Extract offshore vessel fleet data from Offshore Magazine survey PDFs | archived | medium | frontierdeepwater | - |
| WRK-358 | Enrich vessel fleet data with online research — current fleet status + newer surveys | archived | high | frontierdeepwater | - |
| WRK-359 | Design and build vessel marine-parameters database for engineering analysis | archived | high | frontierdeepwater | - |
| WRK-361 | Heriberto: powder room sink caulk for water drainage | in_progress | simple | achantas-data | - |
| WRK-365 | worldenergydata root cleanup — modules/, validators/, tests/agent_os/ | archived | simple | worldenergydata | - |
| WRK-366 | assethold root cleanup — .agent-os/, business/, agents/, empty dirs | archived | medium | assethold | - |
| WRK-367 | assetutilities src/ cleanup — orphaned src/modules/ and src/validators/ | archived | simple | assetutilities | - |
| WRK-368 | Create repo-structure skill — canonical source layout for all tier-1 repos | archived | simple | workspace-hub | - |
| WRK-370 | Heriberto: garage fence door repair | pending | simple | achantas-data | - |
| WRK-371 | Heriberto: powder room faucet tightening | pending | simple | achantas-data | - |
| WRK-373 | Vision document — bridge current repo mission to autonomous-production future | archived | complex | workspace-hub | - |
| WRK-375 | Incorporate SPE Drillbotics mission into ACE Engineering vision and strategy | archived | medium | workspace-hub, digitalmodel | - |
| WRK-376 | Casing/tubing triaxial stress design envelope check (von Mises, API DF, anisotropic grades) | done | medium | digitalmodel | - |
| WRK-379 | Drilling dysfunction detector — stick-slip, washout, bit balling, kick logic | done | simple | digitalmodel | - |
| WRK-380 | Multi-physics simulation chain — Gmsh → OpenFOAM → OrcaFlex as agent-executable pipeline | done | complex | workspace-hub, digitalmodel | - |
| WRK-381 | Trust architecture document — formalise plan gate governance for agent-executed actions | done | simple | workspace-hub | - |
| WRK-386 | Automated Gap-to-WRK Generator — doc → module gaps spawn new work items | done | medium | workspace-hub | - |
| WRK-388 | GIS skills — QGIS, Google Earth Engine, Python GIS ecosystem | done | complex | workspace-hub | - |
| WRK-389 | fix(ace-linux-2): switch Claude install from sudo-npm to native installer | pending | medium | - | - |
| WRK-393 | Evaluate Polymathic AI — The Well for ecosystem integration | done | medium | workspace-hub | - |
| WRK-417 | The Well — planetswe dataset integration with worldenergydata/metocean | done | medium | worldenergydata, digitalmodel | - |
| WRK-418 | The Well — acoustic_scattering datasets for subsea NDE validation | done | medium | digitalmodel | - |
| WRK-419 | The Well — shear_flow dataset for hydrodynamics ML baseline | done | medium | digitalmodel | - |
| WRK-473 | feat(hydrodynamics): integrate wavespectra library for spectral processing | pending | simple | digitalmodel | hydrodynamics/wave_spectra |
| WRK-474 | feat(subsea): integrate MoorDyn + MoorPy for mooring analysis | pending | moderate | digitalmodel | subsea/mooring_analysis |
| WRK-475 | feat(marine_ops): wire Open-Meteo Marine API into weather-window module | pending | simple | digitalmodel | marine_ops/marine_analysis |
| WRK-477 | feat(worldenergydata): create Offshore Geohazard Feed module using USGS API | pending | simple | worldenergydata | safety_analysis/geohazard |
| WRK-479 | feat(worldenergydata): wire SODIR FactPages OData API | pending | moderate | worldenergydata | sodir |
| WRK-480 | feat(worldenergydata): integrate CMEMS Wave Multi-Year Product | pending | moderate | worldenergydata | metocean |
| WRK-483 | feat(digitalmodel/cathodic_protection): Implement ASTM G80 — ASTM G80 (1998) Std Test Method for Specific Catho | pending | low | digitalmodel | - |
| WRK-484 | feat(digitalmodel/cathodic_protection): Implement ASTM G42 — ASTM G42 (1996) Std Test Method for Cathodic Disbo | pending | low | digitalmodel | - |
| WRK-485 | feat(digitalmodel/cathodic_protection): Implement ASTM G95 — ASTM G95 (1998) Std Test Method for Cathodic Disbo | pending | low | digitalmodel | - |
| WRK-486 | feat(digitalmodel/cathodic_protection): Implement ASTM G8 — ASTM G8 (1996) Std Test Methods for Cathodic Disbo | pending | low | digitalmodel | - |
| WRK-487 | feat(digitalmodel/cathodic_protection): Implement ASTM G110 — ASTM G110 (2003) Std Practice for Evaluating Inter | pending | low | digitalmodel | - |
| WRK-541 | feat(digitalmodel/structural): Implement ASTM A131 — ASTM A131 (2004) Std Specification for Structural  | pending | low | digitalmodel | - |
| WRK-542 | feat(OGManufacturing/structural): Implement ASTM A131 — ASTM A131 (2004) Std Specification for Structural  | pending | low | OGManufacturing | - |
| WRK-545 | feat(digitalmodel/structural): Implement ASTM E606 — ASTM E606 (2004) Std Practice for Strain-Controlle | pending | low | digitalmodel | - |
| WRK-546 | feat(OGManufacturing/structural): Implement ASTM E606 — ASTM E606 (2004) Std Practice for Strain-Controlle | pending | low | OGManufacturing | - |
| WRK-549 | feat(digitalmodel/structural): Implement ASTM E466 — ASTM E466 (2002) Std Practice for Conducting Force | pending | low | digitalmodel | - |
| WRK-550 | feat(OGManufacturing/structural): Implement ASTM E466 — ASTM E466 (2002) Std Practice for Conducting Force | pending | low | OGManufacturing | - |
| WRK-551 | feat(digitalmodel/structural): Implement ASTM E739 — ASTM E739 (2004) Std Practice for Statistical Anal | pending | low | digitalmodel | - |
| WRK-552 | feat(OGManufacturing/structural): Implement ASTM E739 — ASTM E739 (2004) Std Practice for Statistical Anal | pending | low | OGManufacturing | - |
| WRK-553 | feat(digitalmodel/structural): Implement ASTM A36 — ASTM A36M-04 (2004) Standard Specification for Car | pending | low | digitalmodel | - |
| WRK-554 | feat(OGManufacturing/structural): Implement ASTM A36 — ASTM A36M-04 (2004) Standard Specification for Car | pending | low | OGManufacturing | - |

### Low

| ID | Title | Status | Complexity | Repos | Module |
|-----|-------|--------|------------|-------|--------|
| WRK-005 | Clean up email using AI (when safe) | pending | medium | achantas-data | - |
| WRK-006 | Upload videos from iPhone to YouTube | blocked | simple | achantas-data | - |
| WRK-008 | Upload photos from multiple devices to achantas-media | pending | medium | achantas-data | - |
| WRK-018 | Extend BSEE field data pipeline to other regulatory sources (RRC, Norway, Mexico, Brazil) | archived | complex | worldenergydata | - |
| WRK-019 | Establish drilling, completion, and intervention cost data by region and environment | done | complex | worldenergydata | - |
| WRK-023 | Property GIS development timeline with future projection and Google Earth animation | in_progress | complex | assethold | - |
| WRK-036 | OrcaFlex structure deployment analysis - supply boat side deployment with structural loads | pending | complex | acma-projects | - |
| WRK-041 | Develop long-term plan for Hobbies repo | done | medium | hobbies | - |
| WRK-042 | Develop long-term plan for Investments repo | done | medium | investments | - |
| WRK-043 | Parametric hull form analysis with RAO generation and client-facing lookup graphs | pending | complex | digitalmodel | - |
| WRK-047 | OpenFOAM CFD analysis capability for digitalmodel | in_progress | complex | digitalmodel | - |
| WRK-048 | Blender working configurations for digitalmodel | pending | medium | digitalmodel | - |
| WRK-055 | aceengineer-website test coverage improvement | archived | simple | aceengineer-website | - |
| WRK-075 | OFFPIPE Integration Module — pipelay cross-validation against OrcaFlex | pending | complex | digitalmodel | - |
| WRK-080 | Write 4 energy data blog posts for SEO | done | complex | aceengineer-website | - |
| WRK-081 | Build interactive NPV calculator for website lead generation | done | complex | aceengineer-website | - |
| WRK-085 | Create public sample data access page on website | done | medium | aceengineer-website | - |
| WRK-088 | Investigate and clean submodule issues (pdf-large-reader, worldenergydata, aceengineercode) | archived | simple | workspace-hub | - |
| WRK-089 | Review Claude Code version gap and update cc-insights | archived | simple | workspace-hub | - |
| WRK-091 | Add dynacard module README | archived | low | digitalmodel | - |
| WRK-092 | Register dynacard CLI entry point | archived | low | digitalmodel | - |
| WRK-093 | Improve dynacard AI diagnostics | archived | complex | digitalmodel | - |
| WRK-101 | Add mesh decimation/coarsening to mesh-utilities skill | done | medium | digitalmodel | - |
| WRK-120 | Research and purchase a smart watch | archived | simple | achantas-data | - |
| WRK-137 | Download and parse rig spec PDFs (102 PDFs from 4 operators) | parked | complex | worldenergydata | - |
| WRK-180 | Stop Hook: Cross-Agent Learning Sync | parked | high | workspace-hub | - |
| WRK-181 | Session Replay & Time Travel | parked | high | workspace-hub | - |
| WRK-182 | Predictive Session Planning | parked | high | workspace-hub | - |
| WRK-193 | UKCS production data module — NSTA/OPRED open data integration (worldenergydata) | archived | moderate | worldenergydata | ukcs |
| WRK-196 | Canada offshore + emerging basin watch list (C-NLOER NL data; Guyana/Suriname/Namibia/Falklands monitor) | archived | moderate | worldenergydata, digitalmodel | canada_offshore + emerging_basins |
| WRK-197 | Nigeria NUPRC + EITI data framework — West Africa deepwater and multi-country payment data | done | moderate | worldenergydata | west_africa |
| WRK-221 | Offshore resilience design framework — modular platforms, lifecycle planning, structural monitoring | done | medium | digitalmodel, aceengineer-website | offshore_resilience |
| WRK-257 | Agent coordination model ADR — document architectural decision record | done | simple | workspace-hub | - |
| WRK-258 | Close WRK-153 as superseded — defer BSEE case study rebuild to after WRK-019 and WRK-171 | archived | simple | worldenergydata | - |
| WRK-262 | Add path-handling guidance to session preflight hook | done | simple | workspace-hub | - |
| WRK-264 | Ensure full work-queue workflow parity between Claude and Codex CLI | done | medium | workspace-hub | - |
| WRK-273 | CP marketing brochure — cathodic protection capability document for aceengineer-website | done | simple | digitalmodel, aceengineer-website | - |
| WRK-288 | Finish ace-linux-2 setup — install open source engineering programs and map capabilities | done | simple | workspace-hub | - |
| WRK-289 | Research open source FEA programs for engineering assignments | done | medium | workspace-hub | - |
| WRK-291 | Install recommended FEA programs on ace-linux-2 | done | medium | workspace-hub | - |
| WRK-292 | Create capability map — file formats, workflow pipelines, interoperability matrix | done | medium | workspace-hub | - |
| WRK-320 | MAIB and NTSB incident correlation with USCG MISLE for root-cause taxonomy | done | high | worldenergydata | - |
| WRK-349 | Document client/portfolio repos in ecosystem docs | done | simple | workspace-hub | - |
| WRK-352 | Set up remote desktop access on ace-linux-2 | working | simple | workspace-hub | - |
| WRK-369 | Remove agent_os references from digitalmodel .claude/ infrastructure | archived | simple | digitalmodel | - |
| WRK-382 | Marketing follow-up — update digitalmodel brochure and aceengineer-website for WRK-373/375 outputs | done | simple | digitalmodel, aceengineer-website | - |
| WRK-390 | enhance(work-queue): richer WRK item presentation in work skill | done | medium | - | - |
| WRK-392 | feat(skills): add work-document-and-exit skill — capture WRK state + session handoff | done | simple | - | - |
| WRK-394 | Planing hull motion model — nonlinear 2D+t strip theory for high-speed vessels | done | complex | digitalmodel | - |
| WRK-402 | worldenergydata test structure consolidation | done | simple | worldenergydata | - |
| WRK-TEST-ENSEMBLE | Smoke test for ensemble planning | pending | simple | workspace-hub | - |

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
| WRK-166 | Jabra USB dongle lost — research universal dongle compatibility | done | medium | - | - |
| WRK-167 | Calendar: Krishna ADHD evaluation — 24 Feb 2:30 PM | done | high | - | - |
| WRK-167 | Calendar: Krishna ADHD evaluation — 24 Feb 2:30 PM | archived | high | - | - |
| WRK-186 | Context budget: trim rules/ to under 16KB | archived | high | workspace-hub | - |
| WRK-207 | Wire model-tier routing into work queue plan.sh and execute.sh — Sonnet 4.6 default, Opus 4.6 for Route C plan only | archived | medium | workspace-hub | - |
| WRK-208 | Cross-platform encoding guard — pre-commit + post-pull encoding validation | archived | high | workspace-hub | - |
| WRK-215 | Graph-aware skill discovery and enhancement — extend /improve with proactive gap analysis | archived | medium | workspace-hub | - |
| WRK-216 | Subagent learning capture — emit signals to pending-reviews before task completion | archived | medium | workspace-hub | - |
| WRK-217 | Update ecosystem-health-check.sh — remove stale skill count threshold | archived | medium | workspace-hub | - |
| WRK-232 | session-bootstrap skill — one-time historical session analysis per machine | archived | high | workspace-hub | - |
| WRK-240 | Diffraction spec converter skill — register as named agent-callable skill | archived | high | digitalmodel | - |
| WRK-244 | OrcaFlex template library skill — get canonical spec.yml by structure type | archived | high | digitalmodel | - |
| WRK-247 | digitalmodel capability manifest — machine-readable module index for agent discovery | archived | medium | digitalmodel | - |
| WRK-252 | worldenergydata module discoverability review — regenerate after new data source modules | archived | medium | worldenergydata | - |
| WRK-255 | Hull library lookup skill — closest-match hull form by target dimensions | archived | medium | digitalmodel | - |
| WRK-257 | Agent coordination model ADR — document architectural decision record | done | low | workspace-hub | - |
| WRK-258 | Close WRK-153 as superseded — defer BSEE case study rebuild to after WRK-019 and WRK-171 | archived | low | worldenergydata | - |
| WRK-262 | Add path-handling guidance to session preflight hook | done | low | workspace-hub | - |
| WRK-270 | Fix cathodic-protection SKILL.md — align examples to real CathodicProtection API | archived | medium | workspace-hub | - |
| WRK-273 | CP marketing brochure — cathodic protection capability document for aceengineer-website | done | low | digitalmodel, aceengineer-website | - |
| WRK-274 | saipem repo content index — searchable catalog of disciplines, project files, and key docs | archived | medium | saipem | - |
| WRK-275 | acma-projects repo content index — catalog projects, codes & standards, and key reference docs | archived | medium | acma-projects | - |
| WRK-278 | Wire legal-sanity-scan into pre-commit for CP-stream repos — activate deny list CI gate | archived | high | digitalmodel, saipem, acma-projects | - |
| WRK-280 | ABS standards acquisition: create folder + download CP Guidance Notes | done | high | workspace-hub | - |
| WRK-280 | ABS standards acquisition: create folder + download CP Guidance Notes | archived | high | workspace-hub | - |
| WRK-281 | Fix 2H legacy project discoverability (navigation layer) | done | medium | workspace-hub | - |
| WRK-282 | Migrate raw ABS docs from O&G-Standards/raw/ into structured ABS/ folder | archived | high | workspace-hub | - |
| WRK-283 | Navigation layer for 0_mrv/, Production/, umbilical/ legacy roots | archived | medium | workspace-hub | - |
| WRK-285 | Write active WRK id to state file on working/ transition | archived | high | workspace-hub | - |
| WRK-286 | Harden chore: commits — require WRK ref for multi-file changes | done | medium | workspace-hub | - |
| WRK-288 | Finish ace-linux-2 setup — install open source engineering programs and map capabilities | done | low | workspace-hub | - |
| WRK-293 | SMART health check on ace-linux-2 drives — install smartmontools + run diagnostics | done | high | workspace-hub | - |
| WRK-294 | Standardize ace-linux-2 mount paths — fstab entries for HDDs with clean paths | in-progress | high | workspace-hub | - |
| WRK-295 | Bidirectional SSH key auth between ace-linux-1 and ace-linux-2 | done | high | workspace-hub | - |
| WRK-296 | Install Tailscale VPN on ace-linux-2 — match ace-linux-1 remote access | done | medium | workspace-hub | - |
| WRK-297 | SSHFS mounts on ace-linux-1 for ace-linux-2 drives — bidirectional file access | pending | high | workspace-hub | - |
| WRK-298 | Install smartmontools on ace-linux-1 + SMART health check on all drives | done | high | workspace-hub | - |
| WRK-307 | Fix KVM display loss on ace-linux-2 after switching — EDID emulator or config fix | archived | medium | workspace-hub | - |
| WRK-341 | Review pdf-large-reader vs native AI agent PDF capabilities — assess continuation or deprecation | done | medium | pdf-large-reader, workspace-hub | - |
| WRK-344 | Remove agent_os from assetutilities | done | high | assetutilities | - |
| WRK-345 | Consolidate validators package into assetutilities | done | high | assetutilities, worldenergydata, assethold | - |
| WRK-346 | Fix aceengineer-admin to standard src/ layout | done | medium | aceengineer-admin | - |
| WRK-347 | Rename aceengineer-website/src/ to content/ | done | medium | aceengineer-website | - |
| WRK-348 | Add root pyproject.toml to workspace-hub src/ | done | medium | workspace-hub | - |
| WRK-349 | Document client/portfolio repos in ecosystem docs | done | low | workspace-hub | - |
| WRK-352 | Set up remote desktop access on ace-linux-2 | working | low | workspace-hub | - |
| WRK-361 | Heriberto: powder room sink caulk for water drainage | in_progress | medium | achantas-data | - |
| WRK-364 | Delete Windows-path directory artifacts in digitalmodel and worldenergydata | archived | high | digitalmodel, worldenergydata | - |
| WRK-365 | worldenergydata root cleanup — modules/, validators/, tests/agent_os/ | archived | medium | worldenergydata | - |
| WRK-367 | assetutilities src/ cleanup — orphaned src/modules/ and src/validators/ | archived | medium | assetutilities | - |
| WRK-368 | Create repo-structure skill — canonical source layout for all tier-1 repos | archived | medium | workspace-hub | - |
| WRK-369 | Remove agent_os references from digitalmodel .claude/ infrastructure | archived | low | digitalmodel | - |
| WRK-370 | Heriberto: garage fence door repair | pending | medium | achantas-data | - |
| WRK-371 | Heriberto: powder room faucet tightening | pending | medium | achantas-data | - |
| WRK-374 | Personal habit — get to the point immediately when asking leaders questions | archived | high | - | - |
| WRK-378 | Generalise CT hydraulics to full wellbore hydraulics module in digitalmodel | done | high | digitalmodel | - |
| WRK-379 | Drilling dysfunction detector — stick-slip, washout, bit balling, kick logic | done | medium | digitalmodel | - |
| WRK-381 | Trust architecture document — formalise plan gate governance for agent-executed actions | done | medium | workspace-hub | - |
| WRK-382 | Marketing follow-up — update digitalmodel brochure and aceengineer-website for WRK-373/375 outputs | done | low | digitalmodel, aceengineer-website | - |
| WRK-392 | feat(skills): add work-document-and-exit skill — capture WRK state + session handoff | done | low | - | - |
| WRK-402 | worldenergydata test structure consolidation | done | low | worldenergydata | - |
| WRK-471 | fix(ace-linux-2): gemini CLI fails on Node 18 with /v regex flag | archived | high | workspace-hub | - |
| WRK-473 | feat(hydrodynamics): integrate wavespectra library for spectral processing | pending | medium | digitalmodel | hydrodynamics/wave_spectra |
| WRK-475 | feat(marine_ops): wire Open-Meteo Marine API into weather-window module | pending | medium | digitalmodel | marine_ops/marine_analysis |
| WRK-477 | feat(worldenergydata): create Offshore Geohazard Feed module using USGS API | pending | medium | worldenergydata | safety_analysis/geohazard |
| WRK-TEST-ENSEMBLE | Smoke test for ensemble planning | pending | low | workspace-hub | - |

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
| WRK-041 | Develop long-term plan for Hobbies repo | done | low | hobbies | - |
| WRK-042 | Develop long-term plan for Investments repo | done | low | investments | - |
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
| WRK-085 | Create public sample data access page on website | done | low | aceengineer-website | - |
| WRK-086 | Rewrite CI workflows for Python/bash workspace | archived | medium | workspace-hub | - |
| WRK-090 | Identify and refactor large files exceeding 400-line limit | archived | medium | workspace-hub | - |
| WRK-096 | Review and improve worldenergydata module structure for discoverability | archived | high | worldenergydata | - |
| WRK-097 | Implement three-tier data residence strategy (worldenergydata ↔ digitalmodel) | archived | high | workspace-hub, worldenergydata, digitalmodel | - |
| WRK-099 | Run 3-way benchmark on Unit Box hull | in_progress | medium | digitalmodel | - |
| WRK-100 | Run 3-way benchmark on Barge hull | archived | medium | digitalmodel | - |
| WRK-101 | Add mesh decimation/coarsening to mesh-utilities skill | done | low | digitalmodel | - |
| WRK-102 | Add generic hull definition/data for all rigs in worldenergydata | archived | medium | worldenergydata | - |
| WRK-103 | Add heavy construction/installation vessel data to worldenergydata | archived | medium | worldenergydata | - |
| WRK-105 | Add drilling riser component data to worldenergydata | archived | medium | worldenergydata | - |
| WRK-108 | Agent usage credits display — show remaining quota at session start for weekly planning | archived | medium | workspace-hub | - |
| WRK-109 | Review, refine, and curate hooks + skills — research best practices from existing workflows | archived | medium | workspace-hub, worldenergydata, digitalmodel | - |
| WRK-113 | Maintain always-current data index with freshness tracking and source metadata | archived | high | worldenergydata | - |
| WRK-115 | Link RAO data to hull shapes in hull library catalog | archived | medium | digitalmodel | - |
| WRK-116 | Scale hull panel meshes to target principal dimensions for hydrodynamic analysis | archived | medium | digitalmodel | - |
| WRK-121 | Extract & Catalog OrcaFlex Models from rock-oil-field/s7 | working | high | workspace-hub | - |
| WRK-122 | Licensed Software Usage Workflow & Burden Reduction | archived | high | acma-projects, assetutilities | - |
| WRK-127 | Sanitize and categorize ideal spec.yml templates for OrcaFlex input across structure types | archived | high | digitalmodel | - |
| WRK-132 | Refine OrcaWave benchmarks: barge/ship/spar RAO fixes + damping/gyradii/Km comparison | archived | high | digitalmodel | - |
| WRK-133 | Update OrcaFlex license agreement with addresses and 3rd-party terms | blocked | high | aceengineer-admin | - |
| WRK-134 | Add future-work brainstorming step before archiving completed items | archived | medium | workspace-hub | - |
| WRK-135 | Ingest XLS historical rig fleet data (163 deepwater rigs) | archived | medium | worldenergydata | - |
| WRK-139 | Develop gmsh skill and documentation | archived | medium | workspace-hub | - |
| WRK-140 | Integrate gmsh meshing skill into digitalmodel and solver pipelines | pending | medium | digitalmodel, workspace-hub | - |
| WRK-141 | Create Achantas family tree to connect all family members | done | medium | achantas-data | - |
| WRK-142 | Review work accomplishments and draft Anthropic outreach message | archived | high | workspace-hub | - |
| WRK-145 | Design code versioning — handle changing revisions of standards | archived | medium | digitalmodel | - |
| WRK-150 | assetutilities test coverage improvement (re-creates WRK-052) | done | medium | assetutilities | - |
| WRK-151 | worldenergydata test coverage improvement (re-creates WRK-054) | archived | medium | worldenergydata | - |
| WRK-152 | Marine safety importer validation — verify MAIB/TSB/IMO/EMSA importers against real data | archived | high | worldenergydata | marine_safety |
| WRK-153 | Energy data case study — BSEE field economics with NPV/IRR workflow | archived | medium | aceengineer-website | - |
| WRK-154 | CI workflow rewrite — fix 2 GitHub Actions workflows | archived | high | workspace-hub | - |
| WRK-158 | Wall thickness parametric engine — Cartesian sweep across D/t, pressure, material | archived | medium | digitalmodel | structural |
| WRK-159 | Three-way design code comparison report — API RP 1111 vs RP 2RD vs STD 2RD | archived | medium | digitalmodel | structural |
| WRK-165 | Research subsea intervention analysis opportunities | done | medium | digitalmodel, worldenergydata | subsea_intervention |
| WRK-169 | Drilling technology evolution — MPD adoption case study | done | medium | aceengineer-website, worldenergydata | content |
| WRK-172 | AI agent usage tracking — real-time quota display, OAuth API, session hooks | archived | high | workspace-hub | ai-tools |
| WRK-175 | Session Start: Engineering Context Loader | done | medium | workspace-hub | - |
| WRK-177 | Stop Hook: Engineering Calculation Audit Trail | archived | high | workspace-hub, worldenergydata | - |
| WRK-178 | Stop Hook: Data Provenance Snapshot | archived | medium | workspace-hub, worldenergydata | - |
| WRK-184 | Improve /improve — Bug fixes, recommendations output, startup readiness | archived | high | workspace-hub | - |
| WRK-185 | Ecosystem Truth Review: instruction/skills/work-item centralization | archived | high | workspace-hub, digitalmodel, worldenergydata | governance |
| WRK-187 | Improve /improve: usage-based skill health, classify retry, apply API content | archived | medium | workspace-hub | - |
| WRK-188 | Wave-1 spec migration: worldenergydata dry-run manifest and apply plan | archived | high | workspace-hub, worldenergydata | governance |
| WRK-199 | AI agent usage optimizer skill — maximize Claude/Codex/Gemini allocation per task | done | medium | workspace-hub | ai-tools |
| WRK-201 | Work queue workflow gate enforcement — plan_reviewed, Route C spec, pre-move checks | archived | high | workspace-hub | work-queue |
| WRK-205 | Skills knowledge graph — capability metadata and relationship layer beyond flat index | archived | medium | workspace-hub | - |
| WRK-206 | Asset integrity / fitness-for-service (FFS) engineering skill — corrosion damage assessment and run-repair-replace decisions | archived | medium | workspace-hub, digitalmodel | - |
| WRK-209 | uv enforcement across workspace — eliminate python3/python fallback chains | archived | medium | workspace-hub | - |
| WRK-211 | Ecosystem health check skill — parallel agent for session and repo-sync workflows | archived | medium | workspace-hub | - |
| WRK-212 | Agent teams protocol skill — orchestrator routing, subagent patterns, team lifecycle | archived | medium | workspace-hub | - |
| WRK-213 | Codex multi-agent roles — assess native role system vs workspace-hub agent skill approach | archived | medium | workspace-hub | - |
| WRK-214 | Session lifecycle compliance — interview-driven review of all workflow scaffolding | archived | high | workspace-hub | - |
| WRK-219 | Batch drilling economics analysis — campaign scheduling and cost optimization | pending | medium | worldenergydata, digitalmodel | drilling_economics |
| WRK-221 | Offshore resilience design framework — modular platforms, lifecycle planning, structural monitoring | done | low | digitalmodel, aceengineer-website | offshore_resilience |
| WRK-225 | Investigate plugins vs skills trade-off for repo ecosystem | archived | medium | workspace-hub | - |
| WRK-226 | Audit and improve agent performance files across Claude, Codex, and Gemini | done | high | workspace-hub | - |
| WRK-226 | Audit and improve agent performance files across Claude, Codex, and Gemini | archived | high | workspace-hub | - |
| WRK-227 | Evaluate cowork relevance — repo ecosystem fit vs agentic coding momentum | parked | medium | workspace-hub | - |
| WRK-228 | Cross-machine terminal UX consistency — Windows Git Bash vs Linux terminal | done | high | - | - |
| WRK-228 | Orient all work items toward agentic AI future-boosting, not just task completion | archived | high | workspace-hub | - |
| WRK-229 | AI agent QA closure — HTML output + SME verification loop per work item | done | high | - | - |
| WRK-229 | Skills curation — online research, knowledge graph review, update index, session-input health check | done | high | workspace-hub | - |
| WRK-229 | Skills curation — online research, knowledge graph review, update index, session-input health check | archived | high | workspace-hub | - |
| WRK-230 | Holistic session lifecycle — unify gap surfacing, stop hooks, and skill input pipeline | archived | high | workspace-hub | - |
| WRK-231 | session-analysis skill — first-class session mining as foundation for skills, gaps, and agent improvement | archived | high | workspace-hub | - |
| WRK-233 | Assess and simplify existing workflows in light of session-analysis self-learning loop | archived | high | workspace-hub | - |
| WRK-236 | Test health trends — track test-writing pairing with code-writing sessions | done | medium | workspace-hub | - |
| WRK-237 | Provider cost tracking — token spend per session and per WRK item | done | medium | workspace-hub | - |
| WRK-238 | Adopt Codex 0.102.0 TOML role definitions — implement native multi-agent roles in .codex/ | done | medium | workspace-hub | - |
| WRK-239 | BSEE field pipeline skill — zero-config agent-callable wrapper | archived | high | worldenergydata | - |
| WRK-241 | Pipeline integrity skill — chain wall thickness, parametric engine, and FFS into one callable workflow | archived | high | digitalmodel | - |
| WRK-242 | Multi-format export as automatic pipeline output stage | archived | high | worldenergydata, digitalmodel | - |
| WRK-243 | Hull analysis setup skill — chain select, scale, mesh, RAO-link into one call | archived | high | digitalmodel | - |
| WRK-245 | Fatigue assessment skill — wrap full module with input schema and auto export | archived | high | digitalmodel | - |
| WRK-246 | LNG terminal dataset — queryable module and aceengineer website data card | archived | medium | worldenergydata, aceengineer-website | - |
| WRK-248 | PHMSA pipeline safety case study — aceengineer website with data-to-assessment workflow | archived | medium | aceengineer-website, worldenergydata | - |
| WRK-249 | ENIGMA safety analysis skill — register as agent-callable capability | archived | medium | worldenergydata | - |
| WRK-250 | Cross-database marine safety case study — MAIB, IMO, EMSA, TSB correlation analysis | archived | medium | worldenergydata, aceengineer-website | - |
| WRK-251 | Dynacard vision model evaluation — benchmark GPT-4V / Claude Vision vs current heuristics | done | medium | digitalmodel | - |
| WRK-253 | Data residence tier compliance audit and extension to assethold | done | medium | worldenergydata, digitalmodel, assethold | - |
| WRK-254 | Heavy vessel GIS integration — connect vessel dataset to GIS skill and BSEE pipeline | done | medium | worldenergydata, digitalmodel | - |
| WRK-259 | BSEE field economics case study — calibrated NPV/IRR with cost data foundation | pending | medium | aceengineer-website, worldenergydata | - |
| WRK-259 | common.units — global unit conversion registry for cross-basin analysis | archived | high | worldenergydata | common.units |
| WRK-261 | BSEE field economics case study — rebuild on calibrated cost data (WRK-019 + WRK-171) | pending | medium | aceengineer-website | - |
| WRK-263 | Progressively reduce agent harness files to ~20 lines by migrating content to skills | done | high | workspace-hub | - |
| WRK-264 | Ensure full work-queue workflow parity between Claude and Codex CLI | done | low | workspace-hub | - |
| WRK-265 | Wire CrossDatabaseAnalyzer to live MAIB/IMO/EMSA/TSB importers | archived | high | worldenergydata | marine_safety |
| WRK-266 | Calibrate decommissioning cost model against BSEE platform removal notices | archived | medium | worldenergydata | decommissioning |
| WRK-267 | Calibrate well planning risk probabilities against BSEE incident and HSE data | archived | medium | worldenergydata | well_planning |
| WRK-268 | Wire ENIGMA safety skill to real HSE incident database for data-driven scoring | archived | medium | worldenergydata | safety_analysis |
| WRK-269 | CP standards research — inventory codes, map version gaps, define implementation scope | archived | high | digitalmodel | - |
| WRK-271 | CP worked examples — end-to-end reference calculations for pipeline, ship, and offshore platform | archived | medium | digitalmodel | - |
| WRK-276 | Abstract all CP client calcs to .md reference — strip project names, keep engineering data, use as tests | archived | high | digitalmodel, saipem, acma-projects | - |
| WRK-279 | Audit & govern the /mnt/ace/ Codex relocation plan | complete | high | workspace-hub | - |
| WRK-279 | Fix DNV_RP_F103_2010 critical defects G-1 through G-4 — replace fabricated table refs + non-standard formulas | archived | critical | digitalmodel | - |
| WRK-287 | Set up Linux-to-Linux network file sharing for workspace-hub access from ace-linux-2 | archived | medium | workspace-hub | - |
| WRK-289 | Research open source FEA programs for engineering assignments | done | low | workspace-hub | - |
| WRK-290 | Install core engineering suite on ace-linux-2 (Blender, OpenFOAM, FreeCAD, Gmsh, BemRosetta) | done | medium | workspace-hub | - |
| WRK-290 | Install core engineering suite on ace-linux-2 (Blender, OpenFOAM, FreeCAD, Gmsh, BemRosetta) | archived | medium | workspace-hub | - |
| WRK-291 | Install recommended FEA programs on ace-linux-2 | done | low | workspace-hub | - |
| WRK-292 | Create capability map — file formats, workflow pipelines, interoperability matrix | done | low | workspace-hub | - |
| WRK-299 | comprehensive-learning skill — single batch command for all session learning + ecosystem improvement | archived | high | - | - |
| WRK-300 | workstations skill — evolve from registry to multi-machine work distribution | archived | medium | - | - |
| WRK-301 | fix: recurring Write correction pattern — not responding to improve | done | medium | - | - |
| WRK-302 | fix: recurring Edit correction pattern — not responding to improve | done | medium | - | - |
| WRK-303 | Ensemble planning — 3×Claude + 3×Codex + 3×Gemini independent agents for non-deterministic plan diversity | archived | medium | workspace-hub | - |
| WRK-304 | cleanup: one lean Stop hook — consume-signals.sh only, all analysis to nightly cron | done | high | - | - |
| WRK-305 | feat: session signal emitters — wire /clear, plan-mode, per-WRK tool-counts | done | medium | - | - |
| WRK-306 | feat: AI agent readiness check — claude/codex/gemini CLI versions + default models | done | medium | - | - |
| WRK-307 | track: lean-session hook requirement missed — accountability record | done | high | - | - |
| WRK-308 | perf: move pre-commit skill validation + readiness checks to nightly cron | done | high | - | - |
| WRK-309 | chore: portable Python invocation — consistent cross-machine execution, zero error noise | archived | high | workspace-hub | - |
| WRK-310 | explore: OrcFxAPI schematic capture for OrcaWave models (program screenshots) | pending | medium | digitalmodel, workspace-hub | - |
| WRK-311 | improve: QTF benchmarking for case 3.1 — charts, comparisons, and validation depth | pending | high | digitalmodel | - |
| WRK-313 | feat: new-machine setup guide + bootstrap script — statusline, CLI parity, cron jobs | done | high | - | - |
| WRK-314 | OrcaFlex Reporting Phase 4 — OrcFxAPI Integration | done | high | - | - |
| WRK-316 | NDBC buoy data ingestion for metocean wave scatter matrices | done | medium | worldenergydata, digitalmodel | - |
| WRK-319 | Real-time EIA and IEA feed ingestion — weekly crude and gas production | done | medium | worldenergydata | - |
| WRK-321 | Field development economics — MIRR NPV with carbon cost sensitivity | done | medium | worldenergydata | - |
| WRK-322 | Fundamentals scoring — P/E P/B EV/EBITDA ranking from yfinance | done | high | assethold | - |
| WRK-323 | Covered call analyser — option chain ingestion and premium yield calculator | done | medium | assethold | - |
| WRK-324 | Risk metrics — VaR CVaR Sharpe ratio max drawdown per position and portfolio | done | high | assethold | - |
| WRK-325 | Sector exposure tracker — auto-classify holdings by GICS sector and flag concentration | done | medium | assethold | - |
| WRK-327 | Shared engineering constants library — material properties unit conversions seawater properties | done | medium | workspace-hub, digitalmodel | - |
| WRK-328 | Agent-readable specs index — YAML index of all specs consumable by AI agents | done | medium | workspace-hub | - |
| WRK-330 | DNV-ST-F101 pressure containment checks for subsea pipelines | done | medium | doris | - |
| WRK-331 | API RP 1111 deepwater pipeline design checks — collapse and propagating buckle | done | medium | doris | - |
| WRK-332 | On-bottom stability module — DNV-RP-F109 soil resistance calculations | done | medium | doris | - |
| WRK-337 | Vessel weather-window calculator — operability analysis from Hs Tp scatter | done | medium | saipem, rock-oil-field | - |
| WRK-338 | LNG tank structural checks — API 620 and EN 14620 thin-shell hoop stress | done | medium | acma-projects | - |
| WRK-339 | Aluminium structural module — Eurocode 9 and AA ADM member capacity checks | done | medium | acma-projects | - |
| WRK-342 | Multi-machine workflow clarity — SSH helper scripts, hostname in statusline, CLI consistency across ace-linux-1 and ace-linux-2 | done | high | workspace-hub | - |
| WRK-343 | OpenFOAM technical debt and exploration — tutorials, ecosystem audit, WRK-047 refresh | pending | medium | workspace-hub, digitalmodel | - |
| WRK-350 | Fix pre-existing test failures in assetutilities | archived | medium | assetutilities | - |
| WRK-351 | Assign workstation to all pending/working/blocked WRK items + bake into planning workflow | archived | high | workspace-hub | - |
| WRK-353 | Expand S-N curve library from 17 to 20 standards | done | high | digitalmodel | - |
| WRK-356 | CP module — sacrificial anode design full calculations per DNV-RP-B401 | done | medium | digitalmodel | - |
| WRK-357 | Extract offshore vessel fleet data from Offshore Magazine survey PDFs | archived | medium | frontierdeepwater | - |
| WRK-360 | Extract contractor contact data + build offshore contractor BD call list | archived | high | frontierdeepwater, aceengineer-admin | - |
| WRK-363 | Audit and deploy cron schedules across all workstations — comprehensive-learning, session-analysis, model-ids, skills-curation | done | high | - | - |
| WRK-366 | assethold root cleanup — .agent-os/, business/, agents/, empty dirs | archived | medium | assethold | - |
| WRK-375 | Incorporate SPE Drillbotics mission into ACE Engineering vision and strategy | archived | medium | workspace-hub, digitalmodel | - |
| WRK-376 | Casing/tubing triaxial stress design envelope check (von Mises, API DF, anisotropic grades) | done | medium | digitalmodel | - |
| WRK-377 | ROP prediction model — Bourgoyne-Young and Warren in digitalmodel | archived | high | digitalmodel | - |
| WRK-383 | Standards-to-Module Capability Map — doc → repo → module linkage | done | high | workspace-hub, digitalmodel, worldenergydata, assetutilities | - |
| WRK-384 | digitalmodel Module Registry — structured metadata for agent-callable modules | done | high | digitalmodel | - |
| WRK-385 | Superintelligent Engineering Agent Architecture — canonical vision and blueprint | done | high | workspace-hub | - |
| WRK-386 | Automated Gap-to-WRK Generator — doc → module gaps spawn new work items | done | medium | workspace-hub | - |
| WRK-389 | fix(ace-linux-2): switch Claude install from sudo-npm to native installer | pending | medium | - | - |
| WRK-390 | enhance(work-queue): richer WRK item presentation in work skill | done | low | - | - |
| WRK-393 | Evaluate Polymathic AI — The Well for ecosystem integration | done | medium | workspace-hub | - |
| WRK-417 | The Well — planetswe dataset integration with worldenergydata/metocean | done | medium | worldenergydata, digitalmodel | - |
| WRK-418 | The Well — acoustic_scattering datasets for subsea NDE validation | done | medium | digitalmodel | - |
| WRK-419 | The Well — shear_flow dataset for hydrodynamics ML baseline | done | medium | digitalmodel | - |
| WRK-422 | feat(assetutilities/calculations): implement 5C — API TR 5C3 (2008) Technical Report on Equations... | done | high | assetutilities | - |
| WRK-423 | feat(assetutilities/calculations): implement API TR 5C3 (2008) Technical Report on... — API TR 5C3 (2008) Technical Report on Equations... | done | high | assetutilities | - |
| WRK-427 | feat(assetutilities/calculations): implement AMJIG, Rev 2 (2000) Deep Water Drilli... — AMJIG, Rev 2 (2000) Deep Water Drilling Riser I... | done | high | assetutilities | - |
| WRK-428 | feat(assetutilities/calculations): implement AMJIG, Rev2 (1999) Deep Water Drillin... — AMJIG, Rev2 (1999) Deep Water Drilling Riser In... | done | high | assetutilities | - |
| WRK-430 | feat(assetutilities/calculations): implement AMJIG, Rev1 (1998) Deep Water Drillin... — AMJIG, Rev1 (1998) Deep Water Drilling Riser In... | done | high | assetutilities | - |
| WRK-437 | feat(assetutilities/calculations): implement BP Riser Array Design Guidelines v2 — BP Riser Array Design Guidelines v2 | done | high | assetutilities | - |
| WRK-470 | feat(gtm): oil-and-gas practitioner persona + 1-month GTM plan for workspace-hub ecosystem | pending | high | workspace-hub | - |
| WRK-488 | feat(digitalmodel/cathodic_protection): Implement ISO 15156 — ISO 15156 Pt 3 1st Ed (2003) Cracking-resistant CR | pending | high | digitalmodel | - |
| WRK-489 | feat(digitalmodel/cathodic_protection): Implement ISO 11881 — ISO 11881 1st Ed (1999) Corrosion of metals and al | pending | high | digitalmodel | - |
| WRK-490 | feat(digitalmodel/cathodic_protection): Implement ISO 11881 — ISO 11881 Corrigendum 1 (1999) Corrosion of metals | pending | high | digitalmodel | - |
| WRK-491 | feat(digitalmodel/cathodic_protection): Implement ISO 15589-2 — ISO15589-2-2004forOR Cathodic Protection | pending | high | digitalmodel | - |
| WRK-492 | feat(digitalmodel/cathodic_protection): Implement ISO 11846 — ISO 11846 1st Ed (1995) Corrosion of metals and al | pending | high | digitalmodel | - |
| WRK-493 | feat(digitalmodel/cathodic_protection): Implement DNV F103 — DNV RP F103 (2010) Cathodic Protection of Submarin | pending | high | digitalmodel | - |
| WRK-494 | feat(digitalmodel/cathodic_protection): Implement DNV F106 — DNV RP F106 (2003) Factory Applied External Pipeli | pending | high | digitalmodel | - |
| WRK-495 | feat(digitalmodel/cathodic_protection): Implement DNV B401 — DNV RP B401 with 2008 amendments (2005) Cathodic P | pending | high | digitalmodel | - |
| WRK-496 | feat(digitalmodel/cathodic_protection): Implement DNV F112 — DNV RP F112 (2008) Stainless steel subsea equipmen | pending | high | digitalmodel | - |
| WRK-501 | feat(digitalmodel/pipeline): Implement ISO 16708 — ISO 16708 1st Ed (2006) Pipeline transportation se | pending | high | digitalmodel | - |
| WRK-502 | feat(doris/pipeline): Implement ISO 16708 — ISO 16708 1st Ed (2006) Pipeline transportation se | pending | high | doris | - |
| WRK-503 | feat(digitalmodel/pipeline): Implement ISO 13628 — ISO 13628 Pt 7 DRAFT (2003) Completion workover ri | pending | high | digitalmodel | - |
| WRK-504 | feat(doris/pipeline): Implement ISO 13628 — ISO 13628 Pt 7 DRAFT (2003) Completion workover ri | pending | high | doris | - |
| WRK-505 | feat(digitalmodel/pipeline): Implement ISO 13624-1 — DIN EN ISO 13624-1 (2007-11) Risers | pending | high | digitalmodel | - |
| WRK-506 | feat(doris/pipeline): Implement ISO 13624-1 — DIN EN ISO 13624-1 (2007-11) Risers | pending | high | doris | - |
| WRK-507 | feat(digitalmodel/pipeline): Implement ISO 13628-7 — ISO 13628-7 2005 Completion Workover Risers | pending | high | digitalmodel | - |
| WRK-508 | feat(doris/pipeline): Implement ISO 13628-7 — ISO 13628-7 2005 Completion Workover Risers | pending | high | doris | - |
| WRK-509 | feat(digitalmodel/pipeline): Implement ISO 16389 — ISO 16389 (2003) Dynamic Risers for Floating Produ | pending | high | digitalmodel | - |
| WRK-510 | feat(doris/pipeline): Implement ISO 16389 — ISO 16389 (2003) Dynamic Risers for Floating Produ | pending | high | doris | - |
| WRK-513 | feat(digitalmodel/pipeline): Implement DNV F101 — DNV OS F101 (2010) Submarine Pipeline Systems | pending | high | digitalmodel | - |
| WRK-514 | feat(doris/pipeline): Implement DNV F101 — DNV OS F101 (2010) Submarine Pipeline Systems | pending | high | doris | - |
| WRK-517 | feat(digitalmodel/pipeline): Implement DNV OSS 006 — DNV OSS 006 (1981) Rules for Submarine Pipeline Sy | pending | high | digitalmodel | - |
| WRK-518 | feat(doris/pipeline): Implement DNV OSS 006 — DNV OSS 006 (1981) Rules for Submarine Pipeline Sy | pending | high | doris | - |
| WRK-519 | feat(digitalmodel/pipeline): Implement DNV F201 — DNV OS F201 (2010) Dynamic Risers | pending | high | digitalmodel | - |
| WRK-520 | feat(doris/pipeline): Implement DNV F201 — DNV OS F201 (2010) Dynamic Risers | pending | high | doris | - |
| WRK-521 | feat(digitalmodel/pipeline): Implement DNV F110 — DNV RP F110 (2007) Global buckling of submarine pi | pending | high | digitalmodel | - |
| WRK-522 | feat(doris/pipeline): Implement DNV F110 — DNV RP F110 (2007) Global buckling of submarine pi | pending | high | doris | - |
| WRK-523 | feat(digitalmodel/pipeline): Implement DNV F108 — DNV RP F108 with update 2009 (2006) Fracture Contr | pending | high | digitalmodel | - |
| WRK-524 | feat(doris/pipeline): Implement DNV F108 — DNV RP F108 with update 2009 (2006) Fracture Contr | pending | high | doris | - |
| WRK-525 | feat(digitalmodel/pipeline): Implement DNV F203 — DNV RP F203 (2009) Riser interference | pending | high | digitalmodel | - |
| WRK-526 | feat(doris/pipeline): Implement DNV F203 — DNV RP F203 (2009) Riser interference | pending | high | doris | - |
| WRK-527 | feat(digitalmodel/pipeline): Implement DNV F105 — DNV RP F105 (2006) Free Spanning Pipelines | pending | high | digitalmodel | - |
| WRK-528 | feat(doris/pipeline): Implement DNV F105 — DNV RP F105 (2006) Free Spanning Pipelines | pending | high | doris | - |
| WRK-529 | feat(digitalmodel/pipeline): Implement DNV F102 — DNV RP F102 (2011) Pipeline Field Joint Coating an | pending | high | digitalmodel | - |
| WRK-530 | feat(doris/pipeline): Implement DNV F102 — DNV RP F102 (2011) Pipeline Field Joint Coating an | pending | high | doris | - |
| WRK-531 | feat(digitalmodel/pipeline): Implement DNV F202 — DNV RP F202 (2010) Composite Risers | pending | high | digitalmodel | - |
| WRK-532 | feat(doris/pipeline): Implement DNV F202 — DNV RP F202 (2010) Composite Risers | pending | high | doris | - |
| WRK-533 | feat(digitalmodel/pipeline): Implement DNV F206 — DNV RP F206 (2008) Riser Integrity Management | pending | high | digitalmodel | - |
| WRK-534 | feat(doris/pipeline): Implement DNV F206 — DNV RP F206 (2008) Riser Integrity Management | pending | high | doris | - |
| WRK-535 | feat(digitalmodel/pipeline): Implement DNV F109 — DNV RP F109 (2007) On-bottom stability design of s | pending | high | digitalmodel | - |
| WRK-536 | feat(doris/pipeline): Implement DNV F109 — DNV RP F109 (2007) On-bottom stability design of s | pending | high | doris | - |
| WRK-537 | feat(digitalmodel/pipeline): Implement DNV F116 — DNV RP F116 (2009) Integrity Management of Submari | pending | high | digitalmodel | - |
| WRK-538 | feat(doris/pipeline): Implement DNV F116 — DNV RP F116 (2009) Integrity Management of Submari | pending | high | doris | - |
| WRK-555 | feat(digitalmodel/marine): Implement DNV E301 — DNV OS E301 (2010) Position Mooring | pending | high | digitalmodel | - |

### Complex

| ID | Title | Status | Priority | Repos | Module |
|-----|-------|--------|----------|-------|--------|
| WRK-011 | Run BSEE analysis for all leases with field nicknames and geological era grouping | archived | high | worldenergydata | - |
| WRK-013 | HSE data analysis to identify typical mishaps by activity and subactivity | archived | high | worldenergydata | - |
| WRK-014 | HSE risk index — client-facing risk insights with risk scoring | archived | medium | worldenergydata | - |
| WRK-015 | Metocean data extrapolation to target locations using GIS and nearest-source modeling | archived | medium | worldenergydata | - |
| WRK-016 | BSEE completion and intervention activity analysis for insights | archived | medium | worldenergydata | - |
| WRK-017 | Streamline BSEE field data analysis pipeline — wellbore, casing, drilling, completions, interventions | archived | high | worldenergydata | - |
| WRK-018 | Extend BSEE field data pipeline to other regulatory sources (RRC, Norway, Mexico, Brazil) | archived | low | worldenergydata | - |
| WRK-019 | Establish drilling, completion, and intervention cost data by region and environment | done | low | worldenergydata | - |
| WRK-020 | GIS skill for cross-application geospatial tools — Blender, QGIS, well plotting | working | medium | digitalmodel | - |
| WRK-021 | Stock analysis for drastic trend changes, technical indicators, and insider trading benchmarks | working | medium | assethold | - |
| WRK-022 | US property valuation analysis using GIS — location, traffic, and spatial factors | done | medium | assethold | - |
| WRK-023 | Property GIS development timeline with future projection and Google Earth animation | in_progress | low | assethold | - |
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
| WRK-047 | OpenFOAM CFD analysis capability for digitalmodel | in_progress | low | digitalmodel | - |
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
| WRK-076 | Add data collection scheduler/orchestrator for automated refresh pipelines | archived | medium | worldenergydata | - |
| WRK-080 | Write 4 energy data blog posts for SEO | done | low | aceengineer-website | - |
| WRK-081 | Build interactive NPV calculator for website lead generation | done | low | aceengineer-website | - |
| WRK-084 | Integrate metocean data sources into unified aggregation interface | archived | medium | worldenergydata | - |
| WRK-087 | Improve test coverage across workspace repos | archived | high | workspace-hub | - |
| WRK-093 | Improve dynacard AI diagnostics | archived | low | digitalmodel | - |
| WRK-094 | Plan, reassess, and improve the workspace-hub workflow | archived | high | workspace-hub | - |
| WRK-104 | Expand drilling rig fleet dataset to all offshore and onshore rigs | archived | high | worldenergydata | - |
| WRK-106 | Hull panel geometry generator from waterline, section, and profile line definitions | done | medium | digitalmodel | - |
| WRK-110 | Expand hull size library with FST, LNGC, and OrcaFlex benchmark shapes | archived | medium | digitalmodel | - |
| WRK-111 | BSEE field development interactive map and analytics | archived | medium | worldenergydata, aceengineer-website | - |
| WRK-112 | Appliance lifecycle analytics module for assethold | done | medium | assethold | - |
| WRK-114 | Collect hull panel shapes and sizes for various floating bodies from existing sources | archived | medium | digitalmodel, worldenergydata | - |
| WRK-117 | Refine and coarsen hull panel meshes for mesh convergence sensitivity analysis | archived | medium | digitalmodel | - |
| WRK-118 | AI agent utilization strategy — leverage Claude, Codex, Gemini for planning, development, testing workflows | working | medium | workspace-hub | - |
| WRK-119 | Test suite optimization — tiered test profiles for commit, task, and session workflows | archived | high | workspace-hub, worldenergydata, digitalmodel | - |
| WRK-126 | Benchmark all example models across time domain and frequency domain with seed equivalence | pending | high | digitalmodel | - |
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | done | high | digitalmodel | - |
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | archived | high | digitalmodel | - |
| WRK-130 | Standardize analysis reporting for each OrcaWave structure type | blocked | high | digitalmodel | - |
| WRK-131 | Passing ship analysis for moored vessels — AQWA-based force calculation and mooring response | working | high | digitalmodel | - |
| WRK-137 | Download and parse rig spec PDFs (102 PDFs from 4 operators) | parked | low | worldenergydata | - |
| WRK-138 | Fitness-for-service module enhancement: wall thickness grid, industry targeting, and asset lifecycle | archived | medium | digitalmodel | asset_integrity |
| WRK-139 | Unified multi-agent orchestration architecture (Claude/Codex/Gemini) | archived | high | workspace-hub | agents |
| WRK-144 | API RP 2RD + API STD 2RD riser wall thickness — WSD & LRFD combined loading | archived | medium | digitalmodel | - |
| WRK-146 | Overhaul aceengineer-website: fix positioning, narrative, and social proof | done | high | aceengineer-website | - |
| WRK-147 | Set up aceengineer-strategy private repo with business operations framework | done | high | aceengineer-strategy | - |
| WRK-148 | ACE-GTM: A&CE Go-to-Market strategy stream | pending | high | aceengineer-website, aceengineer-strategy, workspace-hub | - |
| WRK-149 | digitalmodel test coverage improvement (re-creates WRK-051) | working | high | digitalmodel | - |
| WRK-155 | DNV-ST-F101 submarine pipeline wall thickness — WSD and LRFD methods | archived | high | digitalmodel | structural |
| WRK-156 | FFS Phase 1 — wall thickness grid input with Level 1/2 accept-reject workflow | done | high | digitalmodel | asset_integrity |
| WRK-157 | Fatigue analysis module enhancement — S-N curve reporting and parametric sweeps | archived | high | digitalmodel | fatigue |
| WRK-163 | Well planning risk empowerment framework | archived | medium | worldenergydata, digitalmodel | risk_assessment |
| WRK-164 | Well production test data quality and nodal analysis foundation | archived | high | worldenergydata, digitalmodel | production_engineering |
| WRK-168 | MPD systems knowledge module — pressure management for drillships | archived | high | worldenergydata, digitalmodel | drilling_pressure_management |
| WRK-170 | Integrate MET-OM/metocean-stats as statistical analysis engine for metocean module | archived | medium | worldenergydata, digitalmodel | metocean |
| WRK-171 | Cost data calibration — sanctioned project benchmarking & multivariate cost prediction | pending | medium | worldenergydata | cost |
| WRK-192 | Field development schematic generator — Python SVG/PNG layout diagrams | done | medium | digitalmodel | field_development_visuals |
| WRK-198 | HSE risk index interactive web dashboard | done | medium | aceengineer-website | demos/hse-risk-dashboard.html |
| WRK-200 | Filesystem naming cleanup — eliminate duplicate/conflicting dirs across workspace-hub, digitalmodel, worldenergydata | archived | high | - | - |
| WRK-204 | digitalmodel: rename modules/ naming pattern across docs/, examples/, scripts/python/, base_configs/, tests/ | archived | medium | - | - |
| WRK-218 | Well bore design analysis — slim-hole vs. standard-hole hydraulic and mechanical trade-offs | archived | medium | digitalmodel, worldenergydata | well_design |
| WRK-220 | Offshore decommissioning analytics — data-driven lifecycle planning module | archived | medium | worldenergydata, digitalmodel, aceengineer-website | decommissioning_analytics |
| WRK-234 | MISSION: Self-improving agent ecosystem — sessions drive skills, skills drive better sessions | pending | high | workspace-hub | - |
| WRK-235 | ROADMAP: Repo ecosystem 3-6 month horizon — plan and gear for agentic AI maturation | working | high | workspace-hub | - |
| WRK-256 | Unified parametric study coordinator — orchestrate OrcaFlex, wall thickness, and fatigue sweeps | in-progress | medium | digitalmodel | - |
| WRK-272 | CP capability extension — DNV-RP-B401 offshore platform + DNV-RP-F103 2016 update | archived | medium | digitalmodel | - |
| WRK-277 | CP capability — ABS GN Offshore Structures 2018 route for ABS-classed offshore structures | archived | medium | digitalmodel | - |
| WRK-372 | AI-engineering software interface skills — map and build skills AI agents need to drive engineering programs | archived | high | workspace-hub, digitalmodel | - |
| WRK-373 | Vision document — bridge current repo mission to autonomous-production future | archived | medium | workspace-hub | - |
| WRK-380 | Multi-physics simulation chain — Gmsh → OpenFOAM → OrcaFlex as agent-executable pipeline | done | medium | workspace-hub, digitalmodel | - |
| WRK-387 | Claude Code session auto-refresh with WRK context persistence | done | high | workspace-hub | - |
| WRK-388 | GIS skills — QGIS, Google Earth Engine, Python GIS ecosystem | done | medium | workspace-hub | - |
| WRK-394 | Planing hull motion model — nonlinear 2D+t strip theory for high-speed vessels | done | low | digitalmodel | - |

## By Computer

### ace-linux-1 (271 active / 284 total)

| ID | Title | Status | Priority | Complexity | Repos |
|-----|-------|--------|----------|------------|-------|
| WRK-005 | Clean up email using AI (when safe) | pending | low | medium | achantas-data |
| WRK-006 | Upload videos from iPhone to YouTube | blocked | low | simple | achantas-data |
| WRK-008 | Upload photos from multiple devices to achantas-media | pending | low | medium | achantas-data |
| WRK-019 | Establish drilling, completion, and intervention cost data by region and environment | done | low | complex | worldenergydata |
| WRK-021 | Stock analysis for drastic trend changes, technical indicators, and insider trading benchmarks | working | medium | complex | assethold |
| WRK-022 | US property valuation analysis using GIS — location, traffic, and spatial factors | done | medium | complex | assethold |
| WRK-023 | Property GIS development timeline with future projection and Google Earth animation | in_progress | low | complex | assethold |
| WRK-041 | Develop long-term plan for Hobbies repo | done | low | medium | hobbies |
| WRK-042 | Develop long-term plan for Investments repo | done | low | medium | investments |
| WRK-043 | Parametric hull form analysis with RAO generation and client-facing lookup graphs | pending | low | complex | digitalmodel |
| WRK-050 | Hardware consolidation — inventory, assess, repurpose devices + dev environment readiness | pending | medium | complex | workspace-hub |
| WRK-069 | Acquire USCG MISLE bulk dataset | blocked | high | simple | worldenergydata |
| WRK-080 | Write 4 energy data blog posts for SEO | done | low | complex | aceengineer-website |
| WRK-081 | Build interactive NPV calculator for website lead generation | done | low | complex | aceengineer-website |
| WRK-085 | Create public sample data access page on website | done | low | medium | aceengineer-website |
| WRK-099 | Run 3-way benchmark on Unit Box hull | in_progress | medium | medium | digitalmodel |
| WRK-101 | Add mesh decimation/coarsening to mesh-utilities skill | done | low | medium | digitalmodel |
| WRK-106 | Hull panel geometry generator from waterline, section, and profile line definitions | done | medium | complex | digitalmodel |
| WRK-112 | Appliance lifecycle analytics module for assethold | done | medium | complex | assethold |
| WRK-118 | AI agent utilization strategy — leverage Claude, Codex, Gemini for planning, development, testing workflows | working | medium | complex | workspace-hub |
| WRK-126 | Benchmark all example models across time domain and frequency domain with seed equivalence | pending | high | complex | digitalmodel |
| WRK-137 | Download and parse rig spec PDFs (102 PDFs from 4 operators) | parked | low | complex | worldenergydata |
| WRK-141 | Create Achantas family tree to connect all family members | done | medium | medium | achantas-data |
| WRK-146 | Overhaul aceengineer-website: fix positioning, narrative, and social proof | done | high | complex | aceengineer-website |
| WRK-147 | Set up aceengineer-strategy private repo with business operations framework | done | high | complex | aceengineer-strategy |
| WRK-148 | ACE-GTM: A&CE Go-to-Market strategy stream | pending | high | complex | aceengineer-website, aceengineer-strategy, workspace-hub |
| WRK-149 | digitalmodel test coverage improvement (re-creates WRK-051) | working | high | complex | digitalmodel |
| WRK-150 | assetutilities test coverage improvement (re-creates WRK-052) | done | medium | medium | assetutilities |
| WRK-156 | FFS Phase 1 — wall thickness grid input with Level 1/2 accept-reject workflow | done | high | complex | digitalmodel |
| WRK-165 | Research subsea intervention analysis opportunities | done | medium | medium | digitalmodel, worldenergydata |
| WRK-166 | Jabra USB dongle lost — research universal dongle compatibility | done | medium | simple | - |
| WRK-167 | Calendar: Krishna ADHD evaluation — 24 Feb 2:30 PM | done | high | simple | - |
| WRK-167 | Calendar: Krishna ADHD evaluation — 24 Feb 2:30 PM | archived | high | simple | - |
| WRK-169 | Drilling technology evolution — MPD adoption case study | done | medium | medium | aceengineer-website, worldenergydata |
| WRK-171 | Cost data calibration — sanctioned project benchmarking & multivariate cost prediction | pending | medium | complex | worldenergydata |
| WRK-173 | Session Management Workflow Documentation + Schematic | done | high | low | workspace-hub |
| WRK-175 | Session Start: Engineering Context Loader | done | medium | medium | workspace-hub |
| WRK-176 | Session Start: Design Code Version Guard | done | high | low | workspace-hub, digitalmodel |
| WRK-180 | Stop Hook: Cross-Agent Learning Sync | parked | low | high | workspace-hub |
| WRK-181 | Session Replay & Time Travel | parked | low | high | workspace-hub |
| WRK-182 | Predictive Session Planning | parked | low | high | workspace-hub |
| WRK-183 | Domain Knowledge Graph | done | medium | high | workspace-hub, worldenergydata, digitalmodel |
| WRK-191 | Field development case study catalog — structured reference library of real projects | done | medium | moderate | digitalmodel |
| WRK-192 | Field development schematic generator — Python SVG/PNG layout diagrams | done | medium | complex | digitalmodel |
| WRK-197 | Nigeria NUPRC + EITI data framework — West Africa deepwater and multi-country payment data | done | low | moderate | worldenergydata |
| WRK-198 | HSE risk index interactive web dashboard | done | medium | complex | aceengineer-website |
| WRK-199 | AI agent usage optimizer skill — maximize Claude/Codex/Gemini allocation per task | done | medium | medium | workspace-hub |
| WRK-209 | Add unit validator to EnvironmentSpec.water_density — catch physically implausible values | done | medium | small | digitalmodel |
| WRK-219 | Batch drilling economics analysis — campaign scheduling and cost optimization | pending | medium | medium | worldenergydata, digitalmodel |
| WRK-221 | Offshore resilience design framework — modular platforms, lifecycle planning, structural monitoring | done | low | medium | digitalmodel, aceengineer-website |
| WRK-224 | Tool-readiness SKILL.md — session-start check for CLI, data sources, statusline, work queue | done | medium | low | workspace-hub |
| WRK-226 | Audit and improve agent performance files across Claude, Codex, and Gemini | done | high | medium | workspace-hub |
| WRK-227 | Evaluate cowork relevance — repo ecosystem fit vs agentic coding momentum | parked | medium | medium | workspace-hub |
| WRK-228 | Cross-machine terminal UX consistency — Windows Git Bash vs Linux terminal | done | high | medium | - |
| WRK-229 | AI agent QA closure — HTML output + SME verification loop per work item | done | high | medium | - |
| WRK-229 | Skills curation — online research, knowledge graph review, update index, session-input health check | done | high | medium | workspace-hub |
| WRK-229 | Skills curation — online research, knowledge graph review, update index, session-input health check | archived | high | medium | workspace-hub |
| WRK-234 | MISSION: Self-improving agent ecosystem — sessions drive skills, skills drive better sessions | pending | high | complex | workspace-hub |
| WRK-235 | ROADMAP: Repo ecosystem 3-6 month horizon — plan and gear for agentic AI maturation | working | high | complex | workspace-hub |
| WRK-236 | Test health trends — track test-writing pairing with code-writing sessions | done | medium | medium | workspace-hub |
| WRK-237 | Provider cost tracking — token spend per session and per WRK item | done | medium | medium | workspace-hub |
| WRK-238 | Adopt Codex 0.102.0 TOML role definitions — implement native multi-agent roles in .codex/ | done | medium | medium | workspace-hub |
| WRK-251 | Dynacard vision model evaluation — benchmark GPT-4V / Claude Vision vs current heuristics | done | medium | medium | digitalmodel |
| WRK-253 | Data residence tier compliance audit and extension to assethold | done | medium | medium | worldenergydata, digitalmodel, assethold |
| WRK-254 | Heavy vessel GIS integration — connect vessel dataset to GIS skill and BSEE pipeline | done | medium | medium | worldenergydata, digitalmodel |
| WRK-256 | Unified parametric study coordinator — orchestrate OrcaFlex, wall thickness, and fatigue sweeps | in-progress | medium | complex | digitalmodel |
| WRK-257 | Agent coordination model ADR — document architectural decision record | done | low | simple | workspace-hub |
| WRK-259 | BSEE field economics case study — calibrated NPV/IRR with cost data foundation | pending | medium | medium | aceengineer-website, worldenergydata |
| WRK-261 | BSEE field economics case study — rebuild on calibrated cost data (WRK-019 + WRK-171) | pending | medium | medium | aceengineer-website |
| WRK-262 | Add path-handling guidance to session preflight hook | done | low | simple | workspace-hub |
| WRK-263 | Progressively reduce agent harness files to ~20 lines by migrating content to skills | done | high | medium | workspace-hub |
| WRK-264 | Ensure full work-queue workflow parity between Claude and Codex CLI | done | low | medium | workspace-hub |
| WRK-273 | CP marketing brochure — cathodic protection capability document for aceengineer-website | done | low | simple | digitalmodel, aceengineer-website |
| WRK-279 | Audit & govern the /mnt/ace/ Codex relocation plan | complete | high | medium | workspace-hub |
| WRK-280 | ABS standards acquisition: create folder + download CP Guidance Notes | done | high | simple | workspace-hub |
| WRK-280 | ABS standards acquisition: create folder + download CP Guidance Notes | archived | high | simple | workspace-hub |
| WRK-281 | Fix 2H legacy project discoverability (navigation layer) | done | medium | simple | workspace-hub |
| WRK-286 | Harden chore: commits — require WRK ref for multi-file changes | done | medium | simple | workspace-hub |
| WRK-288 | Finish ace-linux-2 setup — install open source engineering programs and map capabilities | done | low | simple | workspace-hub |
| WRK-289 | Research open source FEA programs for engineering assignments | done | low | medium | workspace-hub |
| WRK-291 | Install recommended FEA programs on ace-linux-2 | done | low | medium | workspace-hub |
| WRK-292 | Create capability map — file formats, workflow pipelines, interoperability matrix | done | low | medium | workspace-hub |
| WRK-297 | SSHFS mounts on ace-linux-1 for ace-linux-2 drives — bidirectional file access | pending | high | simple | workspace-hub |
| WRK-298 | Install smartmontools on ace-linux-1 + SMART health check on all drives | done | high | simple | workspace-hub |
| WRK-301 | fix: recurring Write correction pattern — not responding to improve | done | medium | medium | - |
| WRK-302 | fix: recurring Edit correction pattern — not responding to improve | done | medium | medium | - |
| WRK-304 | cleanup: one lean Stop hook — consume-signals.sh only, all analysis to nightly cron | done | high | medium | - |
| WRK-305 | feat: session signal emitters — wire /clear, plan-mode, per-WRK tool-counts | done | medium | medium | - |
| WRK-306 | feat: AI agent readiness check — claude/codex/gemini CLI versions + default models | done | medium | medium | - |
| WRK-307 | track: lean-session hook requirement missed — accountability record | done | high | medium | - |
| WRK-316 | NDBC buoy data ingestion for metocean wave scatter matrices | done | medium | medium | worldenergydata, digitalmodel |
| WRK-317 | Integrated web dashboard — Plotly Dash for BSEE and FDAS data | done | medium | high | worldenergydata |
| WRK-319 | Real-time EIA and IEA feed ingestion — weekly crude and gas production | done | medium | medium | worldenergydata |
| WRK-320 | MAIB and NTSB incident correlation with USCG MISLE for root-cause taxonomy | done | low | high | worldenergydata |
| WRK-321 | Field development economics — MIRR NPV with carbon cost sensitivity | done | medium | medium | worldenergydata |
| WRK-322 | Fundamentals scoring — P/E P/B EV/EBITDA ranking from yfinance | done | high | medium | assethold |
| WRK-323 | Covered call analyser — option chain ingestion and premium yield calculator | done | medium | medium | assethold |
| WRK-324 | Risk metrics — VaR CVaR Sharpe ratio max drawdown per position and portfolio | done | high | medium | assethold |
| WRK-325 | Sector exposure tracker — auto-classify holdings by GICS sector and flag concentration | done | medium | medium | assethold |
| WRK-326 | Unified CLI — single ace command routing to all repo tools | done | medium | high | workspace-hub |
| WRK-327 | Shared engineering constants library — material properties unit conversions seawater properties | done | medium | medium | workspace-hub, digitalmodel |
| WRK-328 | Agent-readable specs index — YAML index of all specs consumable by AI agents | done | medium | medium | workspace-hub |
| WRK-329 | Formalise doris calculation workflow — migrate ad-hoc calcs to Python modules | done | medium | high | doris |
| WRK-330 | DNV-ST-F101 pressure containment checks for subsea pipelines | done | medium | medium | doris |
| WRK-331 | API RP 1111 deepwater pipeline design checks — collapse and propagating buckle | done | medium | medium | doris |
| WRK-332 | On-bottom stability module — DNV-RP-F109 soil resistance calculations | done | medium | medium | doris |
| WRK-335 | Drilling engineering module — casing design checks per API TR 5C3 | done | medium | high | OGManufacturing |
| WRK-337 | Vessel weather-window calculator — operability analysis from Hs Tp scatter | done | medium | medium | saipem, rock-oil-field |
| WRK-338 | LNG tank structural checks — API 620 and EN 14620 thin-shell hoop stress | done | medium | medium | acma-projects |
| WRK-339 | Aluminium structural module — Eurocode 9 and AA ADM member capacity checks | done | medium | medium | acma-projects |
| WRK-340 | Composite panel design tool — Classical Laminate Theory CLT strength checks | done | medium | high | acma-projects |
| WRK-341 | Review pdf-large-reader vs native AI agent PDF capabilities — assess continuation or deprecation | done | medium | simple | pdf-large-reader, workspace-hub |
| WRK-344 | Remove agent_os from assetutilities | done | high | simple | assetutilities |
| WRK-345 | Consolidate validators package into assetutilities | done | high | simple | assetutilities, worldenergydata, assethold |
| WRK-346 | Fix aceengineer-admin to standard src/ layout | done | medium | simple | aceengineer-admin |
| WRK-347 | Rename aceengineer-website/src/ to content/ | done | medium | simple | aceengineer-website |
| WRK-348 | Add root pyproject.toml to workspace-hub src/ | done | medium | simple | workspace-hub |
| WRK-349 | Document client/portfolio repos in ecosystem docs | done | low | simple | workspace-hub |
| WRK-350 | Fix pre-existing test failures in assetutilities | archived | medium | medium | assetutilities |
| WRK-351 | Assign workstation to all pending/working/blocked WRK items + bake into planning workflow | archived | high | medium | workspace-hub |
| WRK-352 | Set up remote desktop access on ace-linux-2 | working | low | simple | workspace-hub |
| WRK-353 | Expand S-N curve library from 17 to 20 standards | done | high | medium | digitalmodel |
| WRK-354 | Structural module — implement jacket and topside analysis | done | high | high | digitalmodel |
| WRK-355 | Pipeline and flexibles module — pressure containment checks | done | medium | high | digitalmodel |
| WRK-356 | CP module — sacrificial anode design full calculations per DNV-RP-B401 | done | medium | medium | digitalmodel |
| WRK-357 | Extract offshore vessel fleet data from Offshore Magazine survey PDFs | archived | medium | medium | frontierdeepwater |
| WRK-358 | Enrich vessel fleet data with online research — current fleet status + newer surveys | archived | medium | high | frontierdeepwater |
| WRK-359 | Design and build vessel marine-parameters database for engineering analysis | archived | medium | high | frontierdeepwater |
| WRK-360 | Extract contractor contact data + build offshore contractor BD call list | archived | high | medium | frontierdeepwater, aceengineer-admin |
| WRK-361 | Heriberto: powder room sink caulk for water drainage | in_progress | medium | simple | achantas-data |
| WRK-363 | Audit and deploy cron schedules across all workstations — comprehensive-learning, session-analysis, model-ids, skills-curation | done | high | medium | - |
| WRK-370 | Heriberto: garage fence door repair | pending | medium | simple | achantas-data |
| WRK-371 | Heriberto: powder room faucet tightening | pending | medium | simple | achantas-data |
| WRK-373 | Vision document — bridge current repo mission to autonomous-production future | archived | medium | complex | workspace-hub |
| WRK-374 | Personal habit — get to the point immediately when asking leaders questions | archived | high | simple | - |
| WRK-375 | Incorporate SPE Drillbotics mission into ACE Engineering vision and strategy | archived | medium | medium | workspace-hub, digitalmodel |
| WRK-376 | Casing/tubing triaxial stress design envelope check (von Mises, API DF, anisotropic grades) | done | medium | medium | digitalmodel |
| WRK-377 | ROP prediction model — Bourgoyne-Young and Warren in digitalmodel | archived | high | medium | digitalmodel |
| WRK-378 | Generalise CT hydraulics to full wellbore hydraulics module in digitalmodel | done | high | simple | digitalmodel |
| WRK-379 | Drilling dysfunction detector — stick-slip, washout, bit balling, kick logic | done | medium | simple | digitalmodel |
| WRK-380 | Multi-physics simulation chain — Gmsh → OpenFOAM → OrcaFlex as agent-executable pipeline | done | medium | complex | workspace-hub, digitalmodel |
| WRK-381 | Trust architecture document — formalise plan gate governance for agent-executed actions | done | medium | simple | workspace-hub |
| WRK-382 | Marketing follow-up — update digitalmodel brochure and aceengineer-website for WRK-373/375 outputs | done | low | simple | digitalmodel, aceengineer-website |
| WRK-383 | Standards-to-Module Capability Map — doc → repo → module linkage | done | high | medium | workspace-hub, digitalmodel, worldenergydata, assetutilities |
| WRK-384 | digitalmodel Module Registry — structured metadata for agent-callable modules | done | high | medium | digitalmodel |
| WRK-385 | Superintelligent Engineering Agent Architecture — canonical vision and blueprint | done | high | medium | workspace-hub |
| WRK-386 | Automated Gap-to-WRK Generator — doc → module gaps spawn new work items | done | medium | medium | workspace-hub |
| WRK-387 | Claude Code session auto-refresh with WRK context persistence | done | high | complex | workspace-hub |
| WRK-390 | enhance(work-queue): richer WRK item presentation in work skill | done | low | medium | - |
| WRK-392 | feat(skills): add work-document-and-exit skill — capture WRK state + session handoff | done | low | simple | - |
| WRK-402 | worldenergydata test structure consolidation | done | low | simple | worldenergydata |
| WRK-417 | The Well — planetswe dataset integration with worldenergydata/metocean | done | medium | medium | worldenergydata, digitalmodel |
| WRK-418 | The Well — acoustic_scattering datasets for subsea NDE validation | done | medium | medium | digitalmodel |
| WRK-419 | The Well — shear_flow dataset for hydrodynamics ML baseline | done | medium | medium | digitalmodel |
| WRK-420 | feat(assetutilities/calculations): implement ISO-TR 10400, 1st Ed (2007) Equations... — ISO TR 10400, 1st Ed (2007) Equations and calcu... | done | high | low | assetutilities |
| WRK-421 | feat(assetutilities/calculations): implement API BULL 5C3 Formulas and Calculation... — API BULL 5C3 Formulas and Calculations for Casi... | done | high | low | assetutilities |
| WRK-422 | feat(assetutilities/calculations): implement 5C — API TR 5C3 (2008) Technical Report on Equations... | done | high | medium | assetutilities |
| WRK-423 | feat(assetutilities/calculations): implement API TR 5C3 (2008) Technical Report on... — API TR 5C3 (2008) Technical Report on Equations... | done | high | medium | assetutilities |
| WRK-424 | feat(assetutilities/calculations): implement ISO-TR_10400,_1st_Ed_(2007)_Equations... — ISO TR 10400, 1st Ed (2007) Equations and calcu... | done | high | low | assetutilities |
| WRK-425 | feat(assetutilities/calculations): implement BS15663 Pt 2 (2001) Life cycle costin... — BS15663 Pt 2 (2001) Life cycle costing   Guidan... | done | high | low | assetutilities |
| WRK-426 | feat(assetutilities/calculations): implement Marine Trasportations_0030-4 — Marine Trasportations 0030 4 | done | high | low | assetutilities |
| WRK-427 | feat(assetutilities/calculations): implement AMJIG, Rev 2 (2000) Deep Water Drilli... — AMJIG, Rev 2 (2000) Deep Water Drilling Riser I... | done | high | medium | assetutilities |
| WRK-428 | feat(assetutilities/calculations): implement AMJIG, Rev2 (1999) Deep Water Drillin... — AMJIG, Rev2 (1999) Deep Water Drilling Riser In... | done | high | medium | assetutilities |
| WRK-429 | feat(assetutilities/calculations): implement rpt001-3 Deep Water Drilling Riser In... — rpt001 3 Deep Water Drilling Riser Integ Manag ... | done | high | low | assetutilities |
| WRK-430 | feat(assetutilities/calculations): implement AMJIG, Rev1 (1998) Deep Water Drillin... — AMJIG, Rev1 (1998) Deep Water Drilling Riser In... | done | high | medium | assetutilities |
| WRK-431 | feat(assetutilities/calculations): implement os-f101[1] — os f101[1] | done | high | low | assetutilities |
| WRK-432 | feat(assetutilities/calculations): implement F101 — DNVOS F101 | done | high | low | assetutilities |
| WRK-433 | feat(assetutilities/calculations): implement BP - Riser drag dat — BP   Riser drag dat | done | high | low | assetutilities |
| WRK-434 | feat(assetutilities/calculations): implement Buoyant Riser_Shear7_Model — Buoyant Riser Shear7 Model | done | high | low | assetutilities |
| WRK-435 | feat(assetutilities/calculations): implement TNE011-1 Overestimation of VIV Fatigu... — TNE011 1 Overestimation of VIV Fatigue Damage f... | done | high | low | assetutilities |
| WRK-436 | feat(assetutilities/calculations): implement TNE012-1 Internal Pressure Effects on... — TNE012 1 Internal Pressure Effects on Riser Ext... | done | high | low | assetutilities |
| WRK-437 | feat(assetutilities/calculations): implement BP Riser Array Design Guidelines v2 — BP Riser Array Design Guidelines v2 | done | high | medium | assetutilities |
| WRK-438 | feat(assetutilities/calculations): implement Riser Equivalencing & De-equivalencing — Riser Equivalencing & De equivalencing | done | high | low | assetutilities |
| WRK-439 | feat(assetutilities/calculations): implement TNE011-1 Overestimation of VIV Fatigu... — TNE011 1 Overestimation of VIV Fatigue Damage f... | done | high | low | assetutilities |
| WRK-440 | feat(assetutilities/calculations): implement Overestimation of VIV Fatigue Damage ... — Overestimation of VIV Fatigue Damage for Single... | done | high | low | assetutilities |
| WRK-441 | feat(assetutilities/calculations): implement TNE004-1 Riser Tow Out Analysis Metho... — TNE004 1 Riser Tow Out Analysis Methodology | done | high | low | assetutilities |
| WRK-442 | feat(assetutilities/calculations): implement Huse, E., Experimental Investigation ... — Huse, E., Experimental Investigation of Deep Se... | done | high | low | assetutilities |
| WRK-443 | feat(assetutilities/calculations): implement Norton, D.J., et al, 1981 - Wind Tunn... — Norton, D.J., et al, 1981   Wind Tunnel Tests o... | done | high | low | assetutilities |
| WRK-444 | feat(assetutilities/calculations): implement Vandiver, J.K., et al, 1987 - Hydrody... — Vandiver, J.K., et al, 1987   Hydrodynamic Damp... | done | high | low | assetutilities |
| WRK-445 | feat(assetutilities/calculations): implement Smith, C.S., et al, 1981 - Residual S... — Smith, C.S., et al, 1981   Residual Strength an... | done | high | low | assetutilities |
| WRK-446 | feat(assetutilities/calculations): implement Javanmardi, K., et al, 1995 - Auger T... — Javanmardi, K., et al, 1995   Auger TLP Well Sy... | done | high | low | assetutilities |
| WRK-447 | feat(assetutilities/calculations): implement Fox, S.A., et al, 1995 - Design Analy... — Fox, S.A., et al, 1995   Design Analysis and Fu... | done | high | low | assetutilities |
| WRK-448 | feat(assetutilities/calculations): implement Larimore, D., et al, 1998 - Case Hist... — Larimore, D., et al, 1998   Case History   Firs... | done | high | low | assetutilities |
| WRK-449 | feat(assetutilities/calculations): implement Allen, D.W., 1995 - Vortex-InducedVib... — Allen, D.W., 1995   Vortex InducedVibration Ana... | done | high | low | assetutilities |
| WRK-450 | feat(assetutilities/calculations): implement Brooks, I.H., 1987 - A Pragmatic Appr... — Brooks, I.H., 1987   A Pragmatic Approach to Vo... | done | high | low | assetutilities |
| WRK-451 | feat(assetutilities/calculations): implement Carminati, J.R., et al, 1999 - Ursa T... — Carminati, J.R., et al, 1999   Ursa TLP Well Sy... | done | high | low | assetutilities |
| WRK-452 | feat(assetutilities/calculations): implement Barton, D.R., et al, 1999 - Genesis P... — Barton, D.R., et al, 1999   Genesis Project   D... | done | high | low | assetutilities |
| WRK-453 | feat(assetutilities/calculations): implement OTC1997-8494 Code Conflicts — OTC1997 8494 Code Conflicts | done | high | low | assetutilities |
| WRK-454 | feat(assetutilities/calculations): implement OTC2001-13109 SCR Fatigue at Low KC — OTC2001 13109 SCR Fatigue at Low KC | done | high | low | assetutilities |
| WRK-455 | feat(assetutilities/calculations): implement Chen, W.C. 1989, Fatigue - Life Predi... — Chen, W.C. 1989, Fatigue   Life Predictions for... | done | high | low | assetutilities |
| WRK-456 | feat(assetutilities/calculations): implement Sweeney, T., et al, 1991 - Behaviour ... — Sweeney, T., et al, 1991   Behaviour of 15ksi S... | done | high | low | assetutilities |
| WRK-457 | feat(assetutilities/calculations): implement Berner, P., et al, 1997 - Neptune Pro... — Berner, P., et al, 1997   Neptune Project   Pro... | done | high | low | assetutilities |
| WRK-458 | feat(assetutilities/calculations): implement Stahl, OTC 3902, Design Methodology f... — Stahl, OTC 3902, Design Methodology for Offshor... | done | high | low | assetutilities |
| WRK-459 | feat(assetutilities/calculations): implement Gardner, T.N., et al, 1982 - Deepwate... — Gardner, T.N., et al, 1982   Deepwater Drilling... | done | high | low | assetutilities |
| WRK-460 | feat(assetutilities/calculations): implement Allen, D.W., 1998 - Vortex-Induced Vi... — Allen, D.W., 1998   Vortex Induced Vibration of... | done | high | low | assetutilities |
| WRK-461 | feat(assetutilities/calculations): implement Kim, Y.Y., et al, 1975 - Analysis of ... — Kim, Y.Y., et al, 1975   Analysis of Simultaneo... | done | high | low | assetutilities |
| WRK-462 | feat(assetutilities/calculations): implement Grant, R., 1977 - Riser Fairing for R... — Grant, R., 1977   Riser Fairing for Reduced Dra... | done | high | low | assetutilities |
| WRK-463 | feat(assetutilities/calculations): implement Jacobsen, V., et al, 1996 - Vibration... — Jacobsen, V., et al, 1996   Vibration Suppressi... | done | high | low | assetutilities |
| WRK-464 | feat(assetutilities/calculations): implement D'Souza, R., et al, 2002 - The Next G... — D'Souza, R., et al, 2002   The Next Generation ... | done | high | low | assetutilities |
| WRK-465 | feat(assetutilities/calculations): implement Vandiver, J.K., 1985 - The Prediction... — Vandiver, J.K., 1985   The Prediction of Lockin... | done | high | low | assetutilities |
| WRK-466 | feat(assetutilities/calculations): implement Denison, E.B., et al, 1997 - Mars TLP... — Denison, E.B., et al, 1997   Mars TLP Drilling ... | done | high | low | assetutilities |
| WRK-467 | feat(assetutilities/calculations): implement Britton, J.S., et al, 1987 - Improvin... — Britton, J.S., et al, 1987   Improving Wellhead... | done | high | low | assetutilities |
| WRK-468 | feat(assetutilities/calculations): implement Miller, J.E., et al, 1985 - Influence... — Miller, J.E., et al, 1985   Influence of Mud Co... | done | high | low | assetutilities |
| WRK-469 | feat(assetutilities/calculations): implement Imas, L., et al - Sensitivity of SCR ... — Imas, L., et al   Sensitivity of SCR Response a... | done | high | low | assetutilities |
| WRK-470 | feat(gtm): oil-and-gas practitioner persona + 1-month GTM plan for workspace-hub ecosystem | pending | high | medium | workspace-hub |
| WRK-482 | feat(digitalmodel/cathodic_protection): Implement API RP 1632 — API RP 1632 Cathodic Protection of Underground Pet | pending | high | high | digitalmodel |
| WRK-483 | feat(digitalmodel/cathodic_protection): Implement ASTM G80 — ASTM G80 (1998) Std Test Method for Specific Catho | pending | medium | low | digitalmodel |
| WRK-484 | feat(digitalmodel/cathodic_protection): Implement ASTM G42 — ASTM G42 (1996) Std Test Method for Cathodic Disbo | pending | medium | low | digitalmodel |
| WRK-485 | feat(digitalmodel/cathodic_protection): Implement ASTM G95 — ASTM G95 (1998) Std Test Method for Cathodic Disbo | pending | medium | low | digitalmodel |
| WRK-486 | feat(digitalmodel/cathodic_protection): Implement ASTM G8 — ASTM G8 (1996) Std Test Methods for Cathodic Disbo | pending | medium | low | digitalmodel |
| WRK-487 | feat(digitalmodel/cathodic_protection): Implement ASTM G110 — ASTM G110 (2003) Std Practice for Evaluating Inter | pending | medium | low | digitalmodel |
| WRK-488 | feat(digitalmodel/cathodic_protection): Implement ISO 15156 — ISO 15156 Pt 3 1st Ed (2003) Cracking-resistant CR | pending | high | medium | digitalmodel |
| WRK-489 | feat(digitalmodel/cathodic_protection): Implement ISO 11881 — ISO 11881 1st Ed (1999) Corrosion of metals and al | pending | high | medium | digitalmodel |
| WRK-490 | feat(digitalmodel/cathodic_protection): Implement ISO 11881 — ISO 11881 Corrigendum 1 (1999) Corrosion of metals | pending | high | medium | digitalmodel |
| WRK-491 | feat(digitalmodel/cathodic_protection): Implement ISO 15589-2 — ISO15589-2-2004forOR Cathodic Protection | pending | high | medium | digitalmodel |
| WRK-492 | feat(digitalmodel/cathodic_protection): Implement ISO 11846 — ISO 11846 1st Ed (1995) Corrosion of metals and al | pending | high | medium | digitalmodel |
| WRK-493 | feat(digitalmodel/cathodic_protection): Implement DNV F103 — DNV RP F103 (2010) Cathodic Protection of Submarin | pending | high | medium | digitalmodel |
| WRK-494 | feat(digitalmodel/cathodic_protection): Implement DNV F106 — DNV RP F106 (2003) Factory Applied External Pipeli | pending | high | medium | digitalmodel |
| WRK-495 | feat(digitalmodel/cathodic_protection): Implement DNV B401 — DNV RP B401 with 2008 amendments (2005) Cathodic P | pending | high | medium | digitalmodel |
| WRK-496 | feat(digitalmodel/cathodic_protection): Implement DNV F112 — DNV RP F112 (2008) Stainless steel subsea equipmen | pending | high | medium | digitalmodel |
| WRK-497 | feat(digitalmodel/pipeline): Implement API RP 1111 — API RP 1111 | pending | high | high | digitalmodel |
| WRK-498 | feat(doris/pipeline): Implement API RP 1111 — API RP 1111 | pending | high | high | doris |
| WRK-499 | feat(digitalmodel/pipeline): Implement API RP 1109 — API RP 1109 Marking Liquid Petroleum Pipeline Faci | pending | high | high | digitalmodel |
| WRK-500 | feat(doris/pipeline): Implement API RP 1109 — API RP 1109 Marking Liquid Petroleum Pipeline Faci | pending | high | high | doris |
| WRK-501 | feat(digitalmodel/pipeline): Implement ISO 16708 — ISO 16708 1st Ed (2006) Pipeline transportation se | pending | high | medium | digitalmodel |
| WRK-502 | feat(doris/pipeline): Implement ISO 16708 — ISO 16708 1st Ed (2006) Pipeline transportation se | pending | high | medium | doris |
| WRK-503 | feat(digitalmodel/pipeline): Implement ISO 13628 — ISO 13628 Pt 7 DRAFT (2003) Completion workover ri | pending | high | medium | digitalmodel |
| WRK-504 | feat(doris/pipeline): Implement ISO 13628 — ISO 13628 Pt 7 DRAFT (2003) Completion workover ri | pending | high | medium | doris |
| WRK-505 | feat(digitalmodel/pipeline): Implement ISO 13624-1 — DIN EN ISO 13624-1 (2007-11) Risers | pending | high | medium | digitalmodel |
| WRK-506 | feat(doris/pipeline): Implement ISO 13624-1 — DIN EN ISO 13624-1 (2007-11) Risers | pending | high | medium | doris |
| WRK-507 | feat(digitalmodel/pipeline): Implement ISO 13628-7 — ISO 13628-7 2005 Completion Workover Risers | pending | high | medium | digitalmodel |
| WRK-508 | feat(doris/pipeline): Implement ISO 13628-7 — ISO 13628-7 2005 Completion Workover Risers | pending | high | medium | doris |
| WRK-509 | feat(digitalmodel/pipeline): Implement ISO 16389 — ISO 16389 (2003) Dynamic Risers for Floating Produ | pending | high | medium | digitalmodel |
| WRK-510 | feat(doris/pipeline): Implement ISO 16389 — ISO 16389 (2003) Dynamic Risers for Floating Produ | pending | high | medium | doris |
| WRK-511 | feat(digitalmodel/pipeline): Implement API STD 2RD — API STD 2RD 2nd Ed (2013) Dynamic Risers for Float | pending | high | high | digitalmodel |
| WRK-512 | feat(doris/pipeline): Implement API STD 2RD — API STD 2RD 2nd Ed (2013) Dynamic Risers for Float | pending | high | high | doris |
| WRK-513 | feat(digitalmodel/pipeline): Implement DNV F101 — DNV OS F101 (2010) Submarine Pipeline Systems | pending | high | medium | digitalmodel |
| WRK-514 | feat(doris/pipeline): Implement DNV F101 — DNV OS F101 (2010) Submarine Pipeline Systems | pending | high | medium | doris |
| WRK-515 | feat(digitalmodel/pipeline): Implement API RP 17G — API RP 17G 2nd Ed (2006) Design and Operation of C | pending | high | high | digitalmodel |
| WRK-516 | feat(doris/pipeline): Implement API RP 17G — API RP 17G 2nd Ed (2006) Design and Operation of C | pending | high | high | doris |
| WRK-517 | feat(digitalmodel/pipeline): Implement DNV OSS 006 — DNV OSS 006 (1981) Rules for Submarine Pipeline Sy | pending | high | medium | digitalmodel |
| WRK-518 | feat(doris/pipeline): Implement DNV OSS 006 — DNV OSS 006 (1981) Rules for Submarine Pipeline Sy | pending | high | medium | doris |
| WRK-519 | feat(digitalmodel/pipeline): Implement DNV F201 — DNV OS F201 (2010) Dynamic Risers | pending | high | medium | digitalmodel |
| WRK-520 | feat(doris/pipeline): Implement DNV F201 — DNV OS F201 (2010) Dynamic Risers | pending | high | medium | doris |
| WRK-521 | feat(digitalmodel/pipeline): Implement DNV F110 — DNV RP F110 (2007) Global buckling of submarine pi | pending | high | medium | digitalmodel |
| WRK-522 | feat(doris/pipeline): Implement DNV F110 — DNV RP F110 (2007) Global buckling of submarine pi | pending | high | medium | doris |
| WRK-523 | feat(digitalmodel/pipeline): Implement DNV F108 — DNV RP F108 with update 2009 (2006) Fracture Contr | pending | high | medium | digitalmodel |
| WRK-524 | feat(doris/pipeline): Implement DNV F108 — DNV RP F108 with update 2009 (2006) Fracture Contr | pending | high | medium | doris |
| WRK-525 | feat(digitalmodel/pipeline): Implement DNV F203 — DNV RP F203 (2009) Riser interference | pending | high | medium | digitalmodel |
| WRK-526 | feat(doris/pipeline): Implement DNV F203 — DNV RP F203 (2009) Riser interference | pending | high | medium | doris |
| WRK-527 | feat(digitalmodel/pipeline): Implement DNV F105 — DNV RP F105 (2006) Free Spanning Pipelines | pending | high | medium | digitalmodel |
| WRK-528 | feat(doris/pipeline): Implement DNV F105 — DNV RP F105 (2006) Free Spanning Pipelines | pending | high | medium | doris |
| WRK-529 | feat(digitalmodel/pipeline): Implement DNV F102 — DNV RP F102 (2011) Pipeline Field Joint Coating an | pending | high | medium | digitalmodel |
| WRK-530 | feat(doris/pipeline): Implement DNV F102 — DNV RP F102 (2011) Pipeline Field Joint Coating an | pending | high | medium | doris |
| WRK-531 | feat(digitalmodel/pipeline): Implement DNV F202 — DNV RP F202 (2010) Composite Risers | pending | high | medium | digitalmodel |
| WRK-532 | feat(doris/pipeline): Implement DNV F202 — DNV RP F202 (2010) Composite Risers | pending | high | medium | doris |
| WRK-533 | feat(digitalmodel/pipeline): Implement DNV F206 — DNV RP F206 (2008) Riser Integrity Management | pending | high | medium | digitalmodel |
| WRK-534 | feat(doris/pipeline): Implement DNV F206 — DNV RP F206 (2008) Riser Integrity Management | pending | high | medium | doris |
| WRK-535 | feat(digitalmodel/pipeline): Implement DNV F109 — DNV RP F109 (2007) On-bottom stability design of s | pending | high | medium | digitalmodel |
| WRK-536 | feat(doris/pipeline): Implement DNV F109 — DNV RP F109 (2007) On-bottom stability design of s | pending | high | medium | doris |
| WRK-537 | feat(digitalmodel/pipeline): Implement DNV F116 — DNV RP F116 (2009) Integrity Management of Submari | pending | high | medium | digitalmodel |
| WRK-538 | feat(doris/pipeline): Implement DNV F116 — DNV RP F116 (2009) Integrity Management of Submari | pending | high | medium | doris |
| WRK-539 | feat(digitalmodel/structural): Implement API RP 2A — API RP 2A WSD | pending | high | high | digitalmodel |
| WRK-540 | feat(OGManufacturing/structural): Implement API RP 2A — API RP 2A WSD | pending | high | high | OGManufacturing |
| WRK-541 | feat(digitalmodel/structural): Implement ASTM A131 — ASTM A131 (2004) Std Specification for Structural  | pending | medium | low | digitalmodel |
| WRK-542 | feat(OGManufacturing/structural): Implement ASTM A131 — ASTM A131 (2004) Std Specification for Structural  | pending | medium | low | OGManufacturing |
| WRK-543 | feat(digitalmodel/structural): Implement ASTM E1049 — ASTM E1049-85(2005) Standard Practices for Cycle C | pending | high | low | digitalmodel |
| WRK-544 | feat(OGManufacturing/structural): Implement ASTM E1049 — ASTM E1049-85(2005) Standard Practices for Cycle C | pending | high | low | OGManufacturing |
| WRK-545 | feat(digitalmodel/structural): Implement ASTM E606 — ASTM E606 (2004) Std Practice for Strain-Controlle | pending | medium | low | digitalmodel |
| WRK-546 | feat(OGManufacturing/structural): Implement ASTM E606 — ASTM E606 (2004) Std Practice for Strain-Controlle | pending | medium | low | OGManufacturing |
| WRK-547 | feat(digitalmodel/structural): Implement ASTM E647 — ASTM E647 (2005) Std Test Method for Measurement o | pending | high | low | digitalmodel |
| WRK-548 | feat(OGManufacturing/structural): Implement ASTM E647 — ASTM E647 (2005) Std Test Method for Measurement o | pending | high | low | OGManufacturing |
| WRK-549 | feat(digitalmodel/structural): Implement ASTM E466 — ASTM E466 (2002) Std Practice for Conducting Force | pending | medium | low | digitalmodel |
| WRK-550 | feat(OGManufacturing/structural): Implement ASTM E466 — ASTM E466 (2002) Std Practice for Conducting Force | pending | medium | low | OGManufacturing |
| WRK-551 | feat(digitalmodel/structural): Implement ASTM E739 — ASTM E739 (2004) Std Practice for Statistical Anal | pending | medium | low | digitalmodel |
| WRK-552 | feat(OGManufacturing/structural): Implement ASTM E739 — ASTM E739 (2004) Std Practice for Statistical Anal | pending | medium | low | OGManufacturing |
| WRK-553 | feat(digitalmodel/structural): Implement ASTM A36 — ASTM A36M-04 (2004) Standard Specification for Car | pending | medium | low | digitalmodel |
| WRK-554 | feat(OGManufacturing/structural): Implement ASTM A36 — ASTM A36M-04 (2004) Standard Specification for Car | pending | medium | low | OGManufacturing |
| WRK-555 | feat(digitalmodel/marine): Implement DNV E301 — DNV OS E301 (2010) Position Mooring | pending | high | medium | digitalmodel |
| WRK-556 | feat(digitalmodel/marine): Implement API RP 2I — API RP 2I 3rd Ed (2008) In-service Inspection of M | pending | high | high | digitalmodel |
| WRK-557 | feat(digitalmodel/marine): Implement API RP 572 — API RP 572 2nd Ed (2001) Inspection of Pressure Ve | pending | high | high | digitalmodel |
| WRK-558 | feat(digitalmodel/marine): Implement API RP 2SM — API RP 2SM 1st Ed & Addendum (2001 & 2007) Design, | pending | high | high | digitalmodel |
| WRK-559 | feat(digitalmodel/marine): Implement API RP 2P — API RP 2P 2nd Ed (1987) Analysis of Spread Mooring | pending | high | high | digitalmodel |
| WRK-TEST-ENSEMBLE | Smoke test for ensemble planning | pending | low | simple | workspace-hub |

### ace-linux-2 (14 active / 18 total)

| ID | Title | Status | Priority | Complexity | Repos |
|-----|-------|--------|----------|------------|-------|
| WRK-020 | GIS skill for cross-application geospatial tools — Blender, QGIS, well plotting | working | medium | complex | digitalmodel |
| WRK-047 | OpenFOAM CFD analysis capability for digitalmodel | in_progress | low | complex | digitalmodel |
| WRK-048 | Blender working configurations for digitalmodel | pending | low | medium | digitalmodel |
| WRK-140 | Integrate gmsh meshing skill into digitalmodel and solver pipelines | pending | medium | medium | digitalmodel, workspace-hub |
| WRK-290 | Install core engineering suite on ace-linux-2 (Blender, OpenFOAM, FreeCAD, Gmsh, BemRosetta) | done | medium | medium | workspace-hub |
| WRK-290 | Install core engineering suite on ace-linux-2 (Blender, OpenFOAM, FreeCAD, Gmsh, BemRosetta) | archived | medium | medium | workspace-hub |
| WRK-293 | SMART health check on ace-linux-2 drives — install smartmontools + run diagnostics | done | high | simple | workspace-hub |
| WRK-294 | Standardize ace-linux-2 mount paths — fstab entries for HDDs with clean paths | in-progress | high | simple | workspace-hub |
| WRK-295 | Bidirectional SSH key auth between ace-linux-1 and ace-linux-2 | done | high | simple | workspace-hub |
| WRK-296 | Install Tailscale VPN on ace-linux-2 — match ace-linux-1 remote access | done | medium | simple | workspace-hub |
| WRK-307 | Fix KVM display loss on ace-linux-2 after switching — EDID emulator or config fix | archived | medium | simple | workspace-hub |
| WRK-342 | Multi-machine workflow clarity — SSH helper scripts, hostname in statusline, CLI consistency across ace-linux-1 and ace-linux-2 | done | high | medium | workspace-hub |
| WRK-343 | OpenFOAM technical debt and exploration — tutorials, ecosystem audit, WRK-047 refresh | pending | medium | medium | workspace-hub, digitalmodel |
| WRK-372 | AI-engineering software interface skills — map and build skills AI agents need to drive engineering programs | archived | high | complex | workspace-hub, digitalmodel |
| WRK-388 | GIS skills — QGIS, Google Earth Engine, Python GIS ecosystem | done | medium | complex | workspace-hub |
| WRK-389 | fix(ace-linux-2): switch Claude install from sudo-npm to native installer | pending | medium | medium | - |
| WRK-394 | Planing hull motion model — nonlinear 2D+t strip theory for high-speed vessels | done | low | complex | digitalmodel |
| WRK-471 | fix(ace-linux-2): gemini CLI fails on Node 18 with /v regex flag | archived | high | simple | workspace-hub |

### acma-ansys05 (12 active / 12 total)

| ID | Title | Status | Priority | Complexity | Repos |
|-----|-------|--------|----------|------------|-------|
| WRK-032 | Modular OrcaFlex pipeline installation input with parametric campaign support | pending | medium | complex | digitalmodel |
| WRK-036 | OrcaFlex structure deployment analysis - supply boat side deployment with structural loads | pending | low | complex | acma-projects |
| WRK-039 | SPM project benchmarking - AQWA vs OrcaFlex | pending | medium | complex | digitalmodel |
| WRK-045 | OrcaFlex rigid jumper analysis - stress and VIV for various configurations | pending | medium | complex | digitalmodel |
| WRK-046 | OrcaFlex drilling and completion riser parametric analysis | pending | medium | complex | digitalmodel |
| WRK-064 | OrcaFlex format converter: license-required validation and backward-compat wrapper | blocked | medium | medium | digitalmodel |
| WRK-075 | OFFPIPE Integration Module — pipelay cross-validation against OrcaFlex | pending | low | complex | digitalmodel |
| WRK-125 | OrcaFlex module roadmap — evolving coordination and progress tracking | working | high | low | digitalmodel |
| WRK-130 | Standardize analysis reporting for each OrcaWave structure type | blocked | high | complex | digitalmodel |
| WRK-133 | Update OrcaFlex license agreement with addresses and 3rd-party terms | blocked | high | medium | aceengineer-admin |
| WRK-315 | CALM buoy mooring fatigue — spectral fatigue from OrcaFlex time-domain output | done | medium | high | digitalmodel |
| WRK-336 | Portable installation analysis library — extract generic OrcaFlex automation from project code | done | medium | high | saipem, rock-oil-field |

### (unassigned) (13 active / 219 total)

| ID | Title | Status | Priority | Complexity | Repos |
|-----|-------|--------|----------|------------|-------|
| WRK-001 | Repair sink faucet in powder room at 11511 Piping Rock | archived | medium | simple | achantas-data |
| WRK-002 | Stove repair with factory service at 11511 Piping Rock | archived | medium | simple | achantas-data |
| WRK-003 | Garage clean up | archived | medium | simple | achantas-data |
| WRK-004 | Reorganize storage in upstairs bathroom at 11511 Piping Rock | archived | medium | simple | achantas-data |
| WRK-007 | Upload videos from Doris computer to YouTube | archived | medium | simple | achantas-data |
| WRK-009 | Reproduce rev30 lower tertiary BSEE field results for repeatability | archived | high | medium | worldenergydata |
| WRK-010 | Rerun lower tertiary analysis with latest BSEE data and validate | archived | high | medium | worldenergydata |
| WRK-011 | Run BSEE analysis for all leases with field nicknames and geological era grouping | archived | high | complex | worldenergydata |
| WRK-012 | Audit HSE public data coverage and identify gaps | archived | high | medium | worldenergydata |
| WRK-013 | HSE data analysis to identify typical mishaps by activity and subactivity | archived | high | complex | worldenergydata |
| WRK-014 | HSE risk index — client-facing risk insights with risk scoring | archived | medium | complex | worldenergydata |
| WRK-015 | Metocean data extrapolation to target locations using GIS and nearest-source modeling | archived | medium | complex | worldenergydata |
| WRK-016 | BSEE completion and intervention activity analysis for insights | archived | medium | complex | worldenergydata |
| WRK-017 | Streamline BSEE field data analysis pipeline — wellbore, casing, drilling, completions, interventions | archived | high | complex | worldenergydata |
| WRK-018 | Extend BSEE field data pipeline to other regulatory sources (RRC, Norway, Mexico, Brazil) | archived | low | complex | worldenergydata |
| WRK-024 | Buckskin field BSEE data analysis — Keathley Canyon blocks 785, 828, 829, 830, 871, 872 | archived | high | medium | worldenergydata |
| WRK-025 | AQWA diffraction analysis runner | archived | high | complex | digitalmodel |
| WRK-026 | Unified input data format converter for diffraction solvers (AQWA, OrcaWave, BEMRosetta) | archived | high | complex | digitalmodel |
| WRK-027 | AQWA batch analysis execution | archived | high | medium | digitalmodel |
| WRK-028 | AQWA postprocessing - RAOs and verification | archived | high | complex | digitalmodel |
| WRK-029 | OrcaWave diffraction analysis runner + file preparation | archived | high | complex | digitalmodel |
| WRK-030 | OrcaWave batch analysis + postprocessing | archived | high | complex | digitalmodel |
| WRK-031 | Benchmark OrcaWave vs AQWA for 2-3 hulls | archived | medium | complex | digitalmodel |
| WRK-033 | Develop OrcaFlex include-file modular skill for parametrised analysis input | archived | medium | complex | digitalmodel |
| WRK-034 | Develop OrcaWave modular file prep skill for parametrised analysis input | archived | medium | complex | digitalmodel |
| WRK-035 | Develop AQWA modular file prep skill for parametrised analysis input | archived | medium | complex | digitalmodel |
| WRK-037 | Get OrcaFlex framework of agreement and terms | archived | medium | simple | aceengineer-admin |
| WRK-038 | Compile global LNG terminal project dataset with comprehensive parameters | archived | medium | complex | worldenergydata |
| WRK-040 | Mooring benchmarking - AQWA vs OrcaFlex | archived | medium | complex | digitalmodel |
| WRK-044 | Pipeline wall thickness calculations with parametric utilisation analysis | archived | medium | complex | digitalmodel |
| WRK-049 | Determine dynacard module way forward | archived | medium | medium | digitalmodel |
| WRK-051 | digitalmodel test coverage improvement | archived | high | complex | digitalmodel |
| WRK-052 | assetutilities test coverage improvement | archived | high | complex | assetutilities |
| WRK-053 | assethold test coverage improvement | archived | medium | medium | assethold |
| WRK-054 | worldenergydata test coverage improvement | archived | medium | medium | worldenergydata |
| WRK-055 | aceengineer-website test coverage improvement | archived | low | simple | aceengineer-website |
| WRK-056 | aceengineer-admin test coverage improvement | archived | medium | medium | aceengineer-admin |
| WRK-057 | Define canonical spec.yml schema for diffraction analysis | archived | high | medium | digitalmodel |
| WRK-058 | AQWA input backend — spec.yml to single .dat and modular deck files | archived | high | complex | digitalmodel |
| WRK-059 | OrcaWave input backend — spec.yml to single .yml and modular includes | archived | high | complex | digitalmodel |
| WRK-060 | Common mesh format and converter pipeline (BEMRosetta + GMSH) | archived | high | medium | digitalmodel |
| WRK-061 | CLI and integration layer for spec converter | archived | medium | medium | digitalmodel |
| WRK-062 | Test suite for spec converter using existing example data | archived | high | medium | digitalmodel |
| WRK-063 | Reverse parsers — AQWA .dat and OrcaWave .yml to canonical spec.yml | archived | high | complex | digitalmodel |
| WRK-065 | S-lay pipeline installation schema + builders for PRPP Eclipse vessel | archived | high | complex | digitalmodel |
| WRK-066 | Review and improve digitalmodel module structure for discoverability | archived | high | complex | digitalmodel |
| WRK-067 | Acquire OSHA enforcement and fatality data | archived | high | simple | worldenergydata |
| WRK-068 | Acquire BSEE incident investigations and INCs data | archived | high | medium | worldenergydata |
| WRK-070 | Import PHMSA pipeline data and build pipeline_safety module | archived | high | medium | worldenergydata |
| WRK-071 | Acquire NTSB CAROL marine investigations and EPA TRI data | archived | high | simple | worldenergydata |
| WRK-072 | Technical safety analysis module for worldenergydata using ENIGMA theory | archived | high | complex | worldenergydata |
| WRK-073 | Market digitalmodel and worldenergydata capabilities on aceengineer website | archived | high | complex | aceengineer-website |
| WRK-074 | Complete marine safety database importers (MAIB, IMO, EMSA, TSB) | archived | high | complex | worldenergydata |
| WRK-076 | Add data collection scheduler/orchestrator for automated refresh pipelines | archived | medium | complex | worldenergydata |
| WRK-077 | Validate and wire decline curve modeling into BSEE production workflow | archived | high | medium | worldenergydata |
| WRK-078 | Create energy data case study — BSEE field economics with NPV/IRR workflow | archived | medium | medium | aceengineer-website |
| WRK-079 | Create marine safety case study — cross-database incident correlation | archived | medium | medium | aceengineer-website |
| WRK-082 | Complete LNG terminal data pipeline — from config to working collection | archived | medium | medium | worldenergydata |
| WRK-083 | Validate multi-format export (Excel, PDF, Parquet) with real BSEE data | archived | medium | medium | worldenergydata |
| WRK-084 | Integrate metocean data sources into unified aggregation interface | archived | medium | complex | worldenergydata |
| WRK-086 | Rewrite CI workflows for Python/bash workspace | archived | medium | medium | workspace-hub |
| WRK-087 | Improve test coverage across workspace repos | archived | high | complex | workspace-hub |
| WRK-088 | Investigate and clean submodule issues (pdf-large-reader, worldenergydata, aceengineercode) | archived | low | simple | workspace-hub |
| WRK-089 | Review Claude Code version gap and update cc-insights | archived | low | simple | workspace-hub |
| WRK-090 | Identify and refactor large files exceeding 400-line limit | archived | medium | medium | workspace-hub |
| WRK-091 | Add dynacard module README | archived | low | low | digitalmodel |
| WRK-092 | Register dynacard CLI entry point | archived | low | low | digitalmodel |
| WRK-093 | Improve dynacard AI diagnostics | archived | low | complex | digitalmodel |
| WRK-094 | Plan, reassess, and improve the workspace-hub workflow | archived | high | complex | workspace-hub |
| WRK-096 | Review and improve worldenergydata module structure for discoverability | archived | high | medium | worldenergydata |
| WRK-097 | Implement three-tier data residence strategy (worldenergydata ↔ digitalmodel) | archived | high | medium | workspace-hub, worldenergydata, digitalmodel |
| WRK-098 | Clean up 7.1GB large data committed to worldenergydata git history | archived | high | high | worldenergydata |
| WRK-100 | Run 3-way benchmark on Barge hull | archived | medium | medium | digitalmodel |
| WRK-102 | Add generic hull definition/data for all rigs in worldenergydata | archived | medium | medium | worldenergydata |
| WRK-103 | Add heavy construction/installation vessel data to worldenergydata | archived | medium | medium | worldenergydata |
| WRK-104 | Expand drilling rig fleet dataset to all offshore and onshore rigs | archived | high | complex | worldenergydata |
| WRK-105 | Add drilling riser component data to worldenergydata | archived | medium | medium | worldenergydata |
| WRK-107 | Clarify Family Dollar 1099-MISC rent amount discrepancy ($50,085.60) | archived | high | simple | sabithaandkrishnaestates |
| WRK-108 | Agent usage credits display — show remaining quota at session start for weekly planning | archived | medium | medium | workspace-hub |
| WRK-109 | Review, refine, and curate hooks + skills — research best practices from existing workflows | archived | medium | medium | workspace-hub, worldenergydata, digitalmodel |
| WRK-110 | Expand hull size library with FST, LNGC, and OrcaFlex benchmark shapes | archived | medium | complex | digitalmodel |
| WRK-111 | BSEE field development interactive map and analytics | archived | medium | complex | worldenergydata, aceengineer-website |
| WRK-113 | Maintain always-current data index with freshness tracking and source metadata | archived | high | medium | worldenergydata |
| WRK-114 | Collect hull panel shapes and sizes for various floating bodies from existing sources | archived | medium | complex | digitalmodel, worldenergydata |
| WRK-115 | Link RAO data to hull shapes in hull library catalog | archived | medium | medium | digitalmodel |
| WRK-116 | Scale hull panel meshes to target principal dimensions for hydrodynamic analysis | archived | medium | medium | digitalmodel |
| WRK-117 | Refine and coarsen hull panel meshes for mesh convergence sensitivity analysis | archived | medium | complex | digitalmodel |
| WRK-119 | Test suite optimization — tiered test profiles for commit, task, and session workflows | archived | high | complex | workspace-hub, worldenergydata, digitalmodel |
| WRK-120 | Research and purchase a smart watch | archived | low | simple | achantas-data |
| WRK-122 | Licensed Software Usage Workflow & Burden Reduction | archived | high | medium | acma-projects, assetutilities |
| WRK-124 | Session 20260211_095832 — 1 file(s) created | archived | medium | low | digitalmodel |
| WRK-127 | Sanitize and categorize ideal spec.yml templates for OrcaFlex input across structure types | archived | high | medium | digitalmodel |
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | done | high | complex | digitalmodel |
| WRK-129 | Standardize analysis reporting for each OrcaFlex structure type | archived | high | complex | digitalmodel |
| WRK-132 | Refine OrcaWave benchmarks: barge/ship/spar RAO fixes + damping/gyradii/Km comparison | archived | high | medium | digitalmodel |
| WRK-134 | Add future-work brainstorming step before archiving completed items | archived | medium | medium | workspace-hub |
| WRK-135 | Ingest XLS historical rig fleet data (163 deepwater rigs) | archived | medium | medium | worldenergydata |
| WRK-138 | Fitness-for-service module enhancement: wall thickness grid, industry targeting, and asset lifecycle | archived | medium | complex | digitalmodel |
| WRK-139 | Develop gmsh skill and documentation | archived | medium | medium | workspace-hub |
| WRK-139 | Unified multi-agent orchestration architecture (Claude/Codex/Gemini) | archived | high | complex | workspace-hub |
| WRK-142 | Review work accomplishments and draft Anthropic outreach message | archived | high | medium | workspace-hub |
| WRK-143 | Full symmetric M-T envelope — closed polygon lens shapes | archived | medium | simple | digitalmodel |
| WRK-144 | API RP 2RD + API STD 2RD riser wall thickness — WSD & LRFD combined loading | archived | medium | complex | digitalmodel |
| WRK-145 | Design code versioning — handle changing revisions of standards | archived | medium | medium | digitalmodel |
| WRK-151 | worldenergydata test coverage improvement (re-creates WRK-054) | archived | medium | medium | worldenergydata |
| WRK-152 | Marine safety importer validation — verify MAIB/TSB/IMO/EMSA importers against real data | archived | high | medium | worldenergydata |
| WRK-153 | Energy data case study — BSEE field economics with NPV/IRR workflow | archived | medium | medium | aceengineer-website |
| WRK-154 | CI workflow rewrite — fix 2 GitHub Actions workflows | archived | high | medium | workspace-hub |
| WRK-155 | DNV-ST-F101 submarine pipeline wall thickness — WSD and LRFD methods | archived | high | complex | digitalmodel |
| WRK-157 | Fatigue analysis module enhancement — S-N curve reporting and parametric sweeps | archived | high | complex | digitalmodel |
| WRK-158 | Wall thickness parametric engine — Cartesian sweep across D/t, pressure, material | archived | medium | medium | digitalmodel |
| WRK-159 | Three-way design code comparison report — API RP 1111 vs RP 2RD vs STD 2RD | archived | medium | medium | digitalmodel |
| WRK-160 | OSHA severe injury + fatality data completion and severity mapping fix | archived | medium | simple | worldenergydata |
| WRK-161 | BSEE Excel statistics re-download and URL importer verification | archived | medium | simple | worldenergydata |
| WRK-163 | Well planning risk empowerment framework | archived | medium | complex | worldenergydata, digitalmodel |
| WRK-164 | Well production test data quality and nodal analysis foundation | archived | high | complex | worldenergydata, digitalmodel |
| WRK-168 | MPD systems knowledge module — pressure management for drillships | archived | high | complex | worldenergydata, digitalmodel |
| WRK-170 | Integrate MET-OM/metocean-stats as statistical analysis engine for metocean module | archived | medium | complex | worldenergydata, digitalmodel |
| WRK-172 | AI agent usage tracking — real-time quota display, OAuth API, session hooks | archived | high | medium | workspace-hub |
| WRK-177 | Stop Hook: Engineering Calculation Audit Trail | archived | high | medium | workspace-hub, worldenergydata |
| WRK-178 | Stop Hook: Data Provenance Snapshot | archived | medium | medium | workspace-hub, worldenergydata |
| WRK-179 | Start Hook: Agent Capacity Pre-flight | archived | medium | low | workspace-hub |
| WRK-184 | Improve /improve — Bug fixes, recommendations output, startup readiness | archived | high | medium | workspace-hub |
| WRK-185 | Ecosystem Truth Review: instruction/skills/work-item centralization | archived | high | medium | workspace-hub, digitalmodel, worldenergydata |
| WRK-186 | Context budget: trim rules/ to under 16KB | archived | high | simple | workspace-hub |
| WRK-187 | Improve /improve: usage-based skill health, classify retry, apply API content | archived | medium | medium | workspace-hub |
| WRK-188 | Wave-1 spec migration: worldenergydata dry-run manifest and apply plan | archived | high | medium | workspace-hub, worldenergydata |
| WRK-190 | NCS production data module — NPD/Sodir open data integration (worldenergydata) | archived | medium | moderate | worldenergydata |
| WRK-193 | UKCS production data module — NSTA/OPRED open data integration (worldenergydata) | archived | low | moderate | worldenergydata |
| WRK-194 | Brazil ANP production data module — well-level monthly CSV integration (worldenergydata) | archived | high | moderate | worldenergydata |
| WRK-195 | EIA US production data module — non-GoM onshore + Alaska integration (worldenergydata) | archived | medium | moderate | worldenergydata |
| WRK-196 | Canada offshore + emerging basin watch list (C-NLOER NL data; Guyana/Suriname/Namibia/Falklands monitor) | archived | low | moderate | worldenergydata, digitalmodel |
| WRK-200 | Filesystem naming cleanup — eliminate duplicate/conflicting dirs across workspace-hub, digitalmodel, worldenergydata | archived | high | complex | - |
| WRK-201 | Work queue workflow gate enforcement — plan_reviewed, Route C spec, pre-move checks | archived | high | medium | workspace-hub |
| WRK-204 | digitalmodel: rename modules/ naming pattern across docs/, examples/, scripts/python/, base_configs/, tests/ | archived | medium | complex | - |
| WRK-205 | Skills knowledge graph — capability metadata and relationship layer beyond flat index | archived | medium | medium | workspace-hub |
| WRK-206 | Asset integrity / fitness-for-service (FFS) engineering skill — corrosion damage assessment and run-repair-replace decisions | archived | medium | medium | workspace-hub, digitalmodel |
| WRK-207 | Skill relationship maintenance — bidirectional linking as enforced process | archived | medium | small | workspace-hub |
| WRK-207 | Wire model-tier routing into work queue plan.sh and execute.sh — Sonnet 4.6 default, Opus 4.6 for Route C plan only | archived | medium | simple | workspace-hub |
| WRK-208 | Cross-platform encoding guard — pre-commit + post-pull encoding validation | archived | high | simple | workspace-hub |
| WRK-209 | uv enforcement across workspace — eliminate python3/python fallback chains | archived | medium | medium | workspace-hub |
| WRK-210 | Interoperability skill — cross-OS standards and health checks for workspace-hub | archived | medium | small | workspace-hub |
| WRK-211 | Ecosystem health check skill — parallel agent for session and repo-sync workflows | archived | medium | medium | workspace-hub |
| WRK-212 | Agent teams protocol skill — orchestrator routing, subagent patterns, team lifecycle | archived | medium | medium | workspace-hub |
| WRK-213 | Codex multi-agent roles — assess native role system vs workspace-hub agent skill approach | archived | medium | medium | workspace-hub |
| WRK-214 | Session lifecycle compliance — interview-driven review of all workflow scaffolding | archived | high | medium | workspace-hub |
| WRK-215 | Graph-aware skill discovery and enhancement — extend /improve with proactive gap analysis | archived | medium | simple | workspace-hub |
| WRK-216 | Subagent learning capture — emit signals to pending-reviews before task completion | archived | medium | simple | workspace-hub |
| WRK-217 | Update ecosystem-health-check.sh — remove stale skill count threshold | archived | medium | simple | workspace-hub |
| WRK-218 | Well bore design analysis — slim-hole vs. standard-hole hydraulic and mechanical trade-offs | archived | medium | complex | digitalmodel, worldenergydata |
| WRK-220 | Offshore decommissioning analytics — data-driven lifecycle planning module | archived | medium | complex | worldenergydata, digitalmodel, aceengineer-website |
| WRK-222 | Pre-clear session snapshot — /save skill + save-snapshot.sh script | archived | medium | low | workspace-hub |
| WRK-223 | Workstations registry — hardware inventory, hardware-info.sh, ace-linux-1 specs | archived | medium | low | workspace-hub |
| WRK-224 | Tool-readiness SKILL.md — session-start check for CLI, data sources, statusline, work queue | archived | medium | low | workspace-hub |
| WRK-225 | Investigate plugins vs skills trade-off for repo ecosystem | archived | medium | medium | workspace-hub |
| WRK-226 | Audit and improve agent performance files across Claude, Codex, and Gemini | archived | high | medium | workspace-hub |
| WRK-228 | Orient all work items toward agentic AI future-boosting, not just task completion | archived | high | medium | workspace-hub |
| WRK-230 | Holistic session lifecycle — unify gap surfacing, stop hooks, and skill input pipeline | archived | high | medium | workspace-hub |
| WRK-231 | session-analysis skill — first-class session mining as foundation for skills, gaps, and agent improvement | archived | high | medium | workspace-hub |
| WRK-232 | session-bootstrap skill — one-time historical session analysis per machine | archived | high | simple | workspace-hub |
| WRK-233 | Assess and simplify existing workflows in light of session-analysis self-learning loop | archived | high | medium | workspace-hub |
| WRK-239 | BSEE field pipeline skill — zero-config agent-callable wrapper | archived | high | medium | worldenergydata |
| WRK-240 | Diffraction spec converter skill — register as named agent-callable skill | archived | high | simple | digitalmodel |
| WRK-241 | Pipeline integrity skill — chain wall thickness, parametric engine, and FFS into one callable workflow | archived | high | medium | digitalmodel |
| WRK-242 | Multi-format export as automatic pipeline output stage | archived | high | medium | worldenergydata, digitalmodel |
| WRK-243 | Hull analysis setup skill — chain select, scale, mesh, RAO-link into one call | archived | high | medium | digitalmodel |
| WRK-244 | OrcaFlex template library skill — get canonical spec.yml by structure type | archived | high | simple | digitalmodel |
| WRK-245 | Fatigue assessment skill — wrap full module with input schema and auto export | archived | high | medium | digitalmodel |
| WRK-246 | LNG terminal dataset — queryable module and aceengineer website data card | archived | medium | medium | worldenergydata, aceengineer-website |
| WRK-247 | digitalmodel capability manifest — machine-readable module index for agent discovery | archived | medium | simple | digitalmodel |
| WRK-248 | PHMSA pipeline safety case study — aceengineer website with data-to-assessment workflow | archived | medium | medium | aceengineer-website, worldenergydata |
| WRK-249 | ENIGMA safety analysis skill — register as agent-callable capability | archived | medium | medium | worldenergydata |
| WRK-250 | Cross-database marine safety case study — MAIB, IMO, EMSA, TSB correlation analysis | archived | medium | medium | worldenergydata, aceengineer-website |
| WRK-252 | worldenergydata module discoverability review — regenerate after new data source modules | archived | medium | simple | worldenergydata |
| WRK-255 | Hull library lookup skill — closest-match hull form by target dimensions | archived | medium | simple | digitalmodel |
| WRK-258 | Close WRK-153 as superseded — defer BSEE case study rebuild to after WRK-019 and WRK-171 | archived | low | simple | worldenergydata |
| WRK-259 | common.units — global unit conversion registry for cross-basin analysis | archived | high | medium | worldenergydata |
| WRK-260 | Cross-regional production data query interface — unified layer across all 8 basins | archived | high | moderate | worldenergydata |
| WRK-265 | Wire CrossDatabaseAnalyzer to live MAIB/IMO/EMSA/TSB importers | archived | high | medium | worldenergydata |
| WRK-266 | Calibrate decommissioning cost model against BSEE platform removal notices | archived | medium | medium | worldenergydata |
| WRK-267 | Calibrate well planning risk probabilities against BSEE incident and HSE data | archived | medium | medium | worldenergydata |
| WRK-268 | Wire ENIGMA safety skill to real HSE incident database for data-driven scoring | archived | medium | medium | worldenergydata |
| WRK-269 | CP standards research — inventory codes, map version gaps, define implementation scope | archived | high | medium | digitalmodel |
| WRK-270 | Fix cathodic-protection SKILL.md — align examples to real CathodicProtection API | archived | medium | simple | workspace-hub |
| WRK-271 | CP worked examples — end-to-end reference calculations for pipeline, ship, and offshore platform | archived | medium | medium | digitalmodel |
| WRK-272 | CP capability extension — DNV-RP-B401 offshore platform + DNV-RP-F103 2016 update | archived | medium | complex | digitalmodel |
| WRK-274 | saipem repo content index — searchable catalog of disciplines, project files, and key docs | archived | medium | simple | saipem |
| WRK-275 | acma-projects repo content index — catalog projects, codes & standards, and key reference docs | archived | medium | simple | acma-projects |
| WRK-276 | Abstract all CP client calcs to .md reference — strip project names, keep engineering data, use as tests | archived | high | medium | digitalmodel, saipem, acma-projects |
| WRK-277 | CP capability — ABS GN Offshore Structures 2018 route for ABS-classed offshore structures | archived | medium | complex | digitalmodel |
| WRK-278 | Wire legal-sanity-scan into pre-commit for CP-stream repos — activate deny list CI gate | archived | high | simple | digitalmodel, saipem, acma-projects |
| WRK-279 | Fix DNV_RP_F103_2010 critical defects G-1 through G-4 — replace fabricated table refs + non-standard formulas | archived | critical | medium | digitalmodel |
| WRK-282 | Migrate raw ABS docs from O&G-Standards/raw/ into structured ABS/ folder | archived | high | simple | workspace-hub |
| WRK-283 | Navigation layer for 0_mrv/, Production/, umbilical/ legacy roots | archived | medium | simple | workspace-hub |
| WRK-285 | Write active WRK id to state file on working/ transition | archived | high | simple | workspace-hub |
| WRK-287 | Set up Linux-to-Linux network file sharing for workspace-hub access from ace-linux-2 | archived | medium | medium | workspace-hub |
| WRK-299 | comprehensive-learning skill — single batch command for all session learning + ecosystem improvement | archived | high | medium | - |
| WRK-300 | workstations skill — evolve from registry to multi-machine work distribution | archived | medium | medium | - |
| WRK-303 | Ensemble planning — 3×Claude + 3×Codex + 3×Gemini independent agents for non-deterministic plan diversity | archived | medium | medium | workspace-hub |
| WRK-309 | chore: portable Python invocation — consistent cross-machine execution, zero error noise | archived | high | medium | workspace-hub |
| WRK-310 | explore: OrcFxAPI schematic capture for OrcaWave models (program screenshots) | pending | medium | medium | digitalmodel, workspace-hub |
| WRK-310 | Daily network-mount readiness check — SSHFS mounts always available on both machines | archived | high | low | workspace-hub |
| WRK-311 | improve: QTF benchmarking for case 3.1 — charts, comparisons, and validation depth | pending | high | medium | digitalmodel |
| WRK-314 | OrcaFlex Reporting Phase 4 — OrcFxAPI Integration | done | high | medium | - |
| WRK-364 | Delete Windows-path directory artifacts in digitalmodel and worldenergydata | archived | high | simple | digitalmodel, worldenergydata |
| WRK-365 | worldenergydata root cleanup — modules/, validators/, tests/agent_os/ | archived | medium | simple | worldenergydata |
| WRK-366 | assethold root cleanup — .agent-os/, business/, agents/, empty dirs | archived | medium | medium | assethold |
| WRK-367 | assetutilities src/ cleanup — orphaned src/modules/ and src/validators/ | archived | medium | simple | assetutilities |
| WRK-368 | Create repo-structure skill — canonical source layout for all tier-1 repos | archived | medium | simple | workspace-hub |
| WRK-369 | Remove agent_os references from digitalmodel .claude/ infrastructure | archived | low | simple | digitalmodel |
| WRK-473 | feat(hydrodynamics): integrate wavespectra library for spectral processing | pending | medium | simple | digitalmodel |
| WRK-474 | feat(subsea): integrate MoorDyn + MoorPy for mooring analysis | pending | medium | moderate | digitalmodel |
| WRK-475 | feat(marine_ops): wire Open-Meteo Marine API into weather-window module | pending | medium | simple | digitalmodel |
| WRK-476 | feat(worldenergydata): create ESG/Carbon Emissions module | pending | high | moderate | worldenergydata |
| WRK-477 | feat(worldenergydata): create Offshore Geohazard Feed module using USGS API | pending | medium | simple | worldenergydata |
| WRK-478 | feat(subsea): create Cathodic Protection module (DNV-RP-B401) | pending | high | moderate | digitalmodel |
| WRK-479 | feat(worldenergydata): wire SODIR FactPages OData API | pending | medium | moderate | worldenergydata |
| WRK-480 | feat(worldenergydata): integrate CMEMS Wave Multi-Year Product | pending | medium | moderate | worldenergydata |
| WRK-481 | feat(digitalmodel): integrate GEBCO_2025 Bathymetry for subsea routing | pending | high | moderate | digitalmodel |

### ace-linux-2, ace-linux-1 (1 active / 1 total)

| ID | Title | Status | Priority | Complexity | Repos |
|-----|-------|--------|----------|------------|-------|
| WRK-393 | Evaluate Polymathic AI — The Well for ecosystem integration | done | medium | medium | workspace-hub |

### any (2 active / 2 total)

| ID | Title | Status | Priority | Complexity | Repos |
|-----|-------|--------|----------|------------|-------|
| WRK-308 | perf: move pre-commit skill validation + readiness checks to nightly cron | done | high | medium | - |
| WRK-313 | feat: new-machine setup guide + bootstrap script — statusline, CLI parity, cron jobs | done | high | medium | - |

### orcaflex-license-machine (2 active / 2 total)

| ID | Title | Status | Priority | Complexity | Repos |
|-----|-------|--------|----------|------------|-------|
| WRK-121 | Extract & Catalog OrcaFlex Models from rock-oil-field/s7 | working | high | medium | workspace-hub |
| WRK-131 | Passing ship analysis for moored vessels — AQWA-based force calculation and mooring response | working | high | complex | digitalmodel |

## Dependencies

| ID | Title | Blocked By | Children | Parent |
|-----|-------|------------|----------|--------|
| WRK-010 | Rerun lower tertiary analysis with latest BSEE data and validate | WRK-009 | - | - |
| WRK-011 | Run BSEE analysis for all leases with field nicknames and geological era grouping | WRK-010 | - | - |
| WRK-013 | HSE data analysis to identify typical mishaps by activity and subactivity | WRK-012 | - | - |
| WRK-014 | HSE risk index — client-facing risk insights with risk scoring | WRK-013 | - | - |
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
| WRK-196 | Canada offshore + emerging basin watch list (C-NLOER NL data; Guyana/Suriname/Namibia/Falklands monitor) | WRK-190 | - | - |
| WRK-215 | Graph-aware skill discovery and enhancement — extend /improve with proactive gap analysis | WRK-205 | - | - |
| WRK-232 | session-bootstrap skill — one-time historical session analysis per machine | WRK-231 | - | - |
| WRK-233 | Assess and simplify existing workflows in light of session-analysis self-learning loop | WRK-231 | - | - |
| WRK-236 | Test health trends — track test-writing pairing with code-writing sessions | WRK-231 | - | - |
| WRK-237 | Provider cost tracking — token spend per session and per WRK item | WRK-231 | - | - |
| WRK-259 | BSEE field economics case study — calibrated NPV/IRR with cost data foundation | WRK-019, WRK-171 | - | - |
| WRK-261 | BSEE field economics case study — rebuild on calibrated cost data (WRK-019 + WRK-171) | WRK-019, WRK-171 | - | - |
| WRK-271 | CP worked examples — end-to-end reference calculations for pipeline, ship, and offshore platform | WRK-276, WRK-279 | - | - |
| WRK-278 | Wire legal-sanity-scan into pre-commit for CP-stream repos — activate deny list CI gate | WRK-276 | - | - |
| WRK-288 | Finish ace-linux-2 setup — install open source engineering programs and map capabilities | WRK-289, WRK-290, WRK-291, WRK-292 | - | - |
| WRK-292 | Create capability map — file formats, workflow pipelines, interoperability matrix | WRK-290, WRK-291 | - | - |
| WRK-297 | SSHFS mounts on ace-linux-1 for ace-linux-2 drives — bidirectional file access | WRK-294 | - | - |
| WRK-358 | Enrich vessel fleet data with online research — current fleet status + newer surveys | WRK-357 | - | - |
| WRK-359 | Design and build vessel marine-parameters database for engineering analysis | WRK-358 | - | - |
| WRK-367 | assetutilities src/ cleanup — orphaned src/modules/ and src/validators/ | WRK-351 | - | - |

