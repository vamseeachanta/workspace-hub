# Semiconductor CAD/FEM Knowledge Base and Job Taxonomy

Issue: #2508  
Parent lane: #2507  
Created: 2026-04-27  
Scope: research/docs-only knowledge base and reusable job-skill matrix for the semiconductor chip-design CAD/FEM career lane.

## Executive Summary

This report defines a practical semiconductor/chip-design CAD + FEM lane that converts existing engineering strengths—FEA, Python automation, technical reporting, and systems thinking—into a portfolio suitable for semiconductor-adjacent roles. The highest-probability bridge is not immediate full custom ASIC ownership; it is a staged path through package thermal/thermo-mechanical analysis, layout/CAD automation, and reproducible open-source EDA flow literacy.

The recommended order remains:

1. #2508 — build this knowledge base and taxonomy.
2. #2511 — create a semiconductor package thermal/thermo-mechanical FEM benchmark.
3. #2510 — build Python layout/CAD automation for chip/package geometries.
4. #2509 — create a reproducible OpenLane/OpenROAD RTL-to-GDS demo report.
5. #2512 — convert the artifacts into a portfolio and job-application packet.

The reusable data artifact is `data/taxonomy/semiconductor-cad-fem-job-skill-matrix.yaml`.

## Role Family Taxonomy

| Role family | Domain | Why it fits | Skills to demonstrate | Portfolio artifact |
|---|---|---|---|---|
| IC Packaging Simulation Engineer | Package FEM / thermal-mechanical analysis | Directly uses FEA, materials, thermal, fatigue, and engineering judgment. | CTE mismatch, thermal resistance, solder/package fatigue screening, mesh/BC verification, Python post-processing. | #2511 package benchmark with assumptions, model checks, and sensitivity plots. |
| Semiconductor Mechanical/Thermal Engineer | Package FEM / thermal-mechanical analysis | Strong bridge from offshore/mechanical FEA into electronics cooling and package reliability. | Heat-transfer boundary conditions, material stackups, reliability-oriented interpretation, DOE, reporting. | Package thermal dashboard and stress/warpage comparison. |
| Advanced Packaging Engineer | Package + layout automation | Connects chiplet/substrate vocabulary to geometry, reliability, and manufacturability tradeoffs. | Heterogeneous integration vocabulary, substrate/package abstraction, thermal-mechanical tradeoffs. | #2510 + #2511 linked geometry-to-FEM path. |
| ASIC/EDA Technical Program Role | EDA flow | Fits engineering coordination and technical-program execution while building silicon-flow vocabulary. | RTL-to-GDS stages, PDK/open-source constraints, reproducibility, milestone risk tracking. | #2509 reproducible flow report with logs and metrics. |
| Physical-design / EDA-flow Learner Track | EDA flow | Builds hands-on literacy in synthesis, place/route, timing, area, and signoff terminology. | Synthesis, floorplan, placement, CTS, routing, DRC/LVS vocabulary, report interpretation. | Tiny RTL-to-GDS runbook and metrics interpretation note. |
| Layout/CAD Automation Track | Layout/CAD automation | Uses Python and CAD automation strengths without requiring proprietary foundry access. | Parametric geometry, GDS/OASIS concepts, reusable Python APIs, KLayout inspection. | #2510 Python layout/CAD demo for package/chip geometries. |

## Local Job Evidence

The local job-market scans include sparse but useful semiconductor-specific hits plus adjacent thermal/FEA roles. These should be treated as market signals, not exhaustive labor-market proof.

| Title | Company | Location | Source file | Relevance |
|---|---|---|---|---|
| Mechanical Engineer with semiconductor exp. | I3 INFOTEK INC | Gloucester, MA | `docs/strategy/gtm/job-market-scan/raw-results/2026-04-20.json` | Direct semiconductor mechanical bridge. |
| IC Packaging Simulation Engineer | Apple | Austin, TX | `docs/strategy/gtm/job-market-scan/raw-results/2026-04-13.json` | Direct package simulation role. |
| Principal Engineer, Advanced Packaging | Marvell | Austin, TX | `docs/strategy/gtm/job-market-scan/raw-results/2026-04-13.json` | Direct advanced packaging role. |
| Packaging Engineer - Micro-Optics/Microelectronics | COKA | San Francisco Bay Area | `docs/strategy/gtm/job-market-scan/raw-results/2026-04-13.json` | Microelectronics packaging role. |
| Sr. Technical Program Manager, ASIC | Amazon Kuiper Manufacturing Enterprises LLC | Sunnyvale, CA | `docs/strategy/gtm/job-market-scan/raw-results/2026-04-02.json` | ASIC program/flow-literacy target. |
| Staff Engineer, Semi Packaging Engineering | Analog Devices | Wilmington, MA | `docs/strategy/gtm/job-market-scan/raw-results/2026-04-13.json` | Direct semiconductor packaging engineering role. |

## Detailed Role Mapping

| Role id | Tools | Local evidence | Source limits | Child / follow-up |
|---|---|---|---|---|
| ic-packaging-simulation | CalculiX, FEniCSx, Elmer, scikit-fem, ParaView, Python | `docs/research/open-source-fea-survey.md`; `docs/research/scikit-fem-eval.md`; `docs/resources/structural-resources.md` | JEDEC and IPC are restricted or not locally ingested; keep use to vocabulary/follow-up until source text is available. | #2511 |
| semiconductor-mechanical-thermal-engineer | FEniCSx, Elmer, CalculiX, Plotly, Pandas | `docs/strategy/gtm/job-market-scan/raw-results/2026-04-20.json` | Local data has one direct semiconductor mechanical row and multiple broader thermal rows; keep relevance labels explicit. | #2511; follow-up electronics-cooling source ingestion |
| advanced-packaging-engineer | GDSFactory, KLayout, Python, CalculiX | `docs/strategy/gtm/job-market-scan/raw-results/2026-04-13.json` | Semiconductor-specific hits are sparse but direct; external open-tool docs ground practice claims. | #2510; #2511 |
| asic-eda-technical-program-role | OpenROAD, OpenLane, OpenROAD-flow-scripts, SkyWater SKY130, GF180MCU, GitHub Actions | `docs/strategy/gtm/job-market-scan/raw-results/2026-04-02.json` | Bridge role; portfolio should show flow literacy rather than production tapeout ownership. | #2509 |
| physical-design-eda-flow-learner-track | OpenROAD, OpenLane, OpenROAD-flow-scripts, Yosys, Magic, KLayout, SkyWater SKY130, GF180MCU | `docs/roadmaps/chip-design-cad-fem-career-roadmap.md` | Use open educational designs and open PDKs unless foundry access exists. | #2509 |
| layout-cad-automation-track | GDSFactory, KLayout, Python, Shapely, pytest | `docs/roadmaps/chip-design-cad-fem-career-roadmap.md` | Generated geometries are demo/educational and should not imply foundry signoff. | #2510 |

## Tool and Practice Map

| Tool/practice | Domain | Source | Accessed | What the source supports |
|---|---|---|---|---|
| OpenROAD | EDA flow | https://openroad.readthedocs.io/ | 2026-04-27 | Integrated open-source physical-design engine for synthesis/place/route/report literacy. |
| OpenROAD-flow-scripts | EDA flow | https://openroad-flow-scripts.readthedocs.io/ | 2026-04-27 | Reproducible reference flow structure and metrics/log artifacts for #2509. |
| OpenLane | EDA flow | https://openlane.readthedocs.io/ | 2026-04-27 | Packaged open-source RTL-to-GDS flow for educational designs and CI-style reproducibility. |
| KLayout | Layout/CAD automation | https://www.klayout.de/doc.html | 2026-04-27 | GDS/OASIS viewing plus scripted macros/checks for layout QA. |
| GDSFactory | Layout/CAD automation | https://gdsfactory.github.io/gdsfactory/ | 2026-04-27 | Python-parametric layout cell generation and reusable component APIs. |
| SkyWater SKY130 PDK | EDA flow / layout | https://github.com/google/skywater-pdk | 2026-04-27 | Open PDK anchor for educational designs and documented constraints. |
| GF180MCU Open PDK | EDA flow / layout | https://gf180mcu-pdk.readthedocs.io/ | 2026-04-27 | Second open PDK reference for portability and comparative flow awareness. |
| CalculiX | Package FEM / thermal-mechanical analysis | `docs/research/open-source-fea-survey.md` | 2026-04-27 | Existing local FEA survey identifies open structural/thermal solver candidates. |
| FEniCSx / scikit-fem | Package FEM / thermal-mechanical analysis | `docs/research/scikit-fem-eval.md` | 2026-04-27 | Python-native FEM experimentation and transparent verification before heavier solver coupling. |

## Domain Workstreams

### EDA flow

The EDA flow lane should focus on literacy and reproducibility: run a tiny open design through an open flow, preserve commands/logs/metrics, and explain each stage. The portfolio claim should be: “I can run, inspect, and communicate an open-source RTL-to-GDS flow and understand the engineering tradeoffs.” It should not claim production tapeout ownership.

Primary issue: #2509.

### Layout/CAD automation

The layout automation lane should demonstrate Python-parametric geometry and inspection. A good #2510 demo is a small set of reusable cells/regions representing die, package, pads/bumps, keepouts, or thermal zones, exported to an inspectable layout artifact and reviewed with KLayout-style checks. This is the best bridge from Python CAD/report automation into semiconductor tooling.

Primary issue: #2510.

### Package FEM / thermal-mechanical analysis

The package FEM lane is the strongest near-term bridge from existing engineering experience. The #2511 benchmark should start with simple, traceable assumptions: material stack, package/die/substrate abstraction, thermal load or temperature delta, constraints, mesh notes, and stress/warpage/temperature interpretation. The important portfolio value is verification discipline and engineering explanation, not numerical sophistication.

Primary issue: #2511.

## JEDEC/IPC access limitations

JEDEC/IPC access limitations: JEDEC reliability documents and IPC electronics-packaging documents are restricted or not locally ingested in this repository. They may be used only as vocabulary and source-acquisition targets until accessible source text is available. This report does not claim detailed standard requirements, compliance, or source extraction from those documents.

Recommended follow-up candidate: create a source-ingestion issue for legally accessible semiconductor packaging standards, open application notes, and public electronics-cooling references. That issue should classify source rights before any requirements are extracted.

## Portfolio Positioning

Recommended positioning for job applications after #2511/#2510/#2509:

- Engineering identity: mechanical/FEA/Python engineer building semiconductor package simulation and open EDA flow literacy.
- Bridge claim: package thermal/thermo-mechanical analysis is the first target because it uses existing FEA strengths and maps directly to semiconductor packaging roles.
- Tooling claim: Python layout/CAD automation and open-source EDA demos show hands-on learning velocity and reproducibility.
- Evidence style: each artifact should include source links, assumptions, validation commands, and limitations.

## Proposed Downstream Issue Updates

No downstream GitHub issue bodies or comments were edited by #2508. The following are proposed updates for later approval/execution:

- #2511: prioritize the first benchmark as a simple die/substrate/package thermal and thermal-stress model with a short verification report and no proprietary standards claims.
- #2510: make the layout/CAD demo produce geometry that can later feed the #2511 package benchmark, such as die outline, substrate zones, pad/ball arrays, and thermal regions.
- #2509: keep the first OpenLane/OpenROAD demo educational and reproducible; preserve logs, configuration, and metrics rather than attempting a complex design.
- #2512: wait until at least #2511 and #2510 exist, then build resume bullets and a portfolio page around verified artifacts.

## Risks and Guardrails

- Scope creep into full ASIC design: keep #2509 educational and evidence-focused.
- Standards overclaiming: do not make JEDEC/IPC requirements claims until sources are locally available and rights are clear.
- Sparse job data: treat the scans as directional evidence and supplement with fresh job research in #2512.
- Tool churn: record source URLs and access dates; avoid depending on exact CLI versions in this taxonomy.

## Acceptance Traceability

| Acceptance criterion | Evidence in this report/data |
|---|---|
| Primary report exists | `docs/reports/semiconductor-cad-fem-knowledge-base.md` |
| YAML matrix exists | `data/taxonomy/semiconductor-cad-fem-job-skill-matrix.yaml` |
| Six role families | Role Family Taxonomy and YAML `role_families` |
| Six+ job evidence rows from three source files | Local Job Evidence and YAML `job_evidence` |
| Eight+ tool/practice rows | Tool and Practice Map and YAML `tool_practices` |
| Domain coverage | EDA flow, Layout/CAD automation, Package FEM / thermal-mechanical analysis sections |
| JEDEC/IPC limitation | JEDEC/IPC access limitations section |
| Child issue mapping | Proposed Downstream Issue Updates maps #2509, #2510, #2511, and #2512; parent #2507 anchors the lane |
