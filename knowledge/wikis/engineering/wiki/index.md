---
domain: engineering
created: 2026-04-08 16:07 UTC
last_updated: 2026-05-03
page_count: 103
source_count: 16
---

# Knowledge Index: Engineering

*Repo engineering methodology — how the workspace-hub ecosystem is built and operated.*
*Updated by LLM during ingest operations.*

## Concepts (52 pages)

| Page | Summary | Last Updated |
|------|---------|-------------|
| [Agent Delegation](concepts/agent-delegation.md) | Spawning focused sub-agents with fresh context for specific tasks | 2026-04-08 |
| [AI Drill Well on Paper](concepts/ai-drill-well-on-paper.md) | GenAI applied to DWOP pre-spud well planning (IADC session) | 2026-04-08 |
| [Canonical Spec Semantic Equivalence Contract](concepts/canonical-spec-semantic-equivalence.md) | Cross-solver semantic equivalence contract for canonical `spec.yml` -> native OrcaWave/OrcaFlex YAML | 2026-04-26 |
| [Cathodic Protection Design](concepts/cathodic-protection-design.md) | CP system design — DNV-RP-B401/F103, anode sizing, ICCP vs sacrificial | 2026-04-08 |
| [CFD Offshore Hydrodynamics](concepts/cfd-offshore-hydrodynamics.md) | OpenFOAM/Fluent for wave loading, Morison, scour, VIV | 2026-04-08 |
| [Compliance Dashboard](concepts/compliance-dashboard.md) | Automated review compliance tracking and reporting | 2026-04-08 |
| [Compliance Enforcement](concepts/compliance-enforcement.md) | Technical infrastructure ensuring agents follow plan-review-implement-ship | 2026-04-08 |
| [Compound Engineering](concepts/compound-engineering.md) | Core methodology — work produces tools, tools produce better work | 2026-04-08 |
| [Compound Learning Loop](concepts/compound-learning-loop.md) | Skills improve from real work, not upfront design — the flywheel | 2026-04-08 |
| [Context Budget Management](concepts/context-budget-management.md) | Managing token cost and context window budget across agent sessions | 2026-04-08 |
| [Energy Field Economics](concepts/energy-field-economics.md) | NPV, Arps decline, fiscal regimes, Monte Carlo P10/P50/P90 | 2026-04-08 |
| [Enforcement Over Instruction](concepts/enforcement-over-instruction.md) | Text-based rules get bypassed; technical gates don't | 2026-04-08 |
| [Fatigue Analysis for Offshore Structures](concepts/fatigue-analysis-offshore.md) | S-N curves, rainflow counting, Miner's rule, spectral fatigue methods | 2026-04-09 |
| [FEA Structural Analysis](concepts/fea-structural-analysis.md) | Meshing, BCs, convergence, hot-spot stress, shell vs solid | 2026-04-08 |
| [Field Development Economics](concepts/field-development-economics.md) | Integrated FDAS/economics from worldenergydata — NPV, fiscal regimes, cost ML | 2026-04-09 |
| [Free-Span VIV Fatigue Assessment](concepts/free-span-viv-fatigue.md) | DNV-RP-F105 clean-room implementation — VIV screening, multi-current damage | 2026-04-09 |
| [Git-Based Pull Queue](concepts/git-based-pull-queue.md) | Async job dispatch across firewall-separated machines using git | 2026-04-08 |
| [Hydrodynamic Analysis](concepts/hydrodynamic-analysis.md) | BEM potential flow — RAOs, added mass, damping, wave excitation, QTFs | 2026-04-09 |
| [JSONL Knowledge Stores](concepts/jsonl-knowledge-stores.md) | Append-only JSONL as lightweight persistent knowledge store | 2026-04-08 |
| [Knowledge-to-Website Pipeline](concepts/knowledge-to-website-pipeline.md) | Turn repo knowledge into aceengineer.com client-facing content | 2026-04-08 |
| [Mooring Line Failure Physics](concepts/mooring-line-failure-physics.md) | HMPE degradation, long-period swell resonance, snap-back, industry statistics | 2026-04-09 |
| [Multi-Agent Parity](concepts/multi-agent-parity.md) | All agents share equal knowledge via git-tracked files | 2026-04-08 |
| [Orchestrator-Worker Separation](concepts/orchestrator-worker-separation.md) | Coordinator + isolated workers beats single-agent context overload | 2026-04-08 |
| [Pile Capacity Alpha Method](concepts/pile-capacity-alpha-method.md) | API RP 2GEO alpha method for axial pile capacity in clay | 2026-04-08 |
| [Pipeline Coatings](concepts/pipeline-coatings.md) | Anti-corrosion, thermal insulation, concrete weight, FJC | 2026-05-03 |
| [Pipeline End-Expansion and Spool Design](concepts/pipeline-end-expansion-spool-design.md) | End-expansion budget, spools, mid-line tees, PLETs/PLEMs | 2026-05-03 |
| [Pipeline Installation Methods](concepts/pipeline-installation-methods.md) | S-lay, J-lay, reel-lay, tow methods for offshore pipelines | 2026-05-03 |
| [Pipeline Integrity Assessment](concepts/pipeline-integrity-assessment.md) | DNV-RP-F101 and API 579 fitness-for-service methods | 2026-04-08 |
| [Pipeline Lateral Buckling](concepts/pipeline-lateral-buckling.md) | Controlled HT/HP lateral buckling — DNV-RP-F110 relief | 2026-05-03 |
| [Pipeline On-Bottom Stability](concepts/pipeline-on-bottom-stability.md) | DNV-RP-F109 — wave/current lateral & vertical stability | 2026-05-03 |
| [Pipeline Route Selection](concepts/pipeline-route-selection.md) | Geohazard avoidance, asset crossings, corridor engineering | 2026-05-03 |
| [Pipeline Soil Interaction](concepts/pipeline-soil-interaction.md) | Axial/lateral/vertical pipe-soil resistance at the seabed | 2026-05-03 |
| [Pipeline Trawl Impact Protection](concepts/pipeline-trawl-impact-protection.md) | Fishing-gear impact, hooking, pull-over, dropped objects | 2026-05-03 |
| [Pipeline Upheaval Buckling](concepts/pipeline-upheaval-buckling.md) | Vertical-plane buckling of buried/trenched HT/HP pipelines | 2026-05-03 |
| [Pipeline Walking](concepts/pipeline-walking.md) | Cumulative axial displacement under thermal cycling | 2026-05-03 |
| [Python Type Safety](concepts/python-type-safety.md) | mypy strict mode, NamedTuple patterns, Optional narrowing | 2026-04-08 |
| [Riser Composite Design](concepts/riser-composite-design.md) | FRP layered architecture, hybrid metallic-composite end fittings | 2026-05-03 |
| [Riser Configurations — Topology](concepts/riser-configurations.md) | Topology hub: free-hanging, lazy-wave, steep-wave, hybrid | 2026-05-03 |
| [Riser Drilling System](concepts/riser-drilling-system.md) | Marine drilling riser stack, slip-joint, LMRP, BOP, FLS | 2026-05-03 |
| [Riser Flexible (Unbonded) Design](concepts/riser-flexible-design.md) | Unbonded flexible-pipe layers, end-fittings, ancillaries | 2026-05-03 |
| [Riser Global-Analysis Load Cases](concepts/riser-global-analysis-load-cases.md) | FLS/ULS/ALS taxonomy crosscutting all riser types | 2026-05-03 |
| [Riser Hybrid Tower / SLOR](concepts/riser-hybrid-tower.md) | Vertical rigid bundle to surface buoy — SLOR / bundled tower | 2026-05-03 |
| [Riser Installation Methods](concepts/riser-installation-methods.md) | Lay, pull-up, splash-zone protection, tie-in to host | 2026-05-03 |
| [Riser Soil Interaction](concepts/riser-soil-interaction.md) | Touchdown-point soil stiffness, trench evolution, SCR fatigue | 2026-05-03 |
| [Riser Steel Catenary (SCR) Design](concepts/riser-steel-catenary-design.md) | Hang-off geometry, TDP migration, FLS sensitivity | 2026-05-03 |
| [Riser Top-Tensioned (TTR) Design](concepts/riser-top-tensioned-design.md) | TLP/spar dry-tree riser — top tensioner, stress joints | 2026-05-03 |
| [Seakeeping and 6-DOF Ship Dynamics](concepts/seakeeping-6dof.md) | 6DOF equations of motion, RAO-based operability, motion criteria | 2026-04-09 |
| [Shell Scripting Patterns](concepts/shell-scripting-patterns.md) | Atomic writes, flock, idempotency, shellcheck, portability | 2026-04-08 |
| [S-N Curve Fatigue Definitions](concepts/sn-curve-fatigue-definitions.md) | S-N curves, DNV-RP-C203 weld categories, Miner's rule | 2026-04-08 |
| [Standards Update Tracking (2025-2026)](concepts/standards-update-tracking.md) | Active standards changes — DNV-RP-C203 2024, ABS consolidation, API 579 Part 16 | 2026-04-09 |
| [Structural Analysis for Offshore Structures](concepts/structural-analysis-offshore.md) | DNV/API/ISO ULS/ALS checks, buckling, tubular joints, stiffened panels | 2026-04-09 |
| [Test-Driven Development](concepts/test-driven-development.md) | TDD mandatory — tests before implementation, no exceptions | 2026-04-08 |
| [Three-Agent Cross-Review](concepts/three-agent-cross-review.md) | Independent reviewers (Claude/Codex/Gemini) for plans and artifacts | 2026-04-08 |
| [VIV Riser Fatigue](concepts/viv-riser-fatigue.md) | OrcaFlex VIV analysis, current discretisation, wake interference | 2026-04-08 |
| [Wave Theory for Offshore Engineering](concepts/wave-theory-offshore.md) | JONSWAP spectra, wave statistics, long-period swell, extreme values | 2026-04-09 |

## Entities (22 pages)

| Page | Summary | Last Updated |
|------|---------|-------------|
| [AQWA Solver](entities/aqwa-solver.md) | ANSYS AQWA hydrodynamic diffraction solver — DAT/LIS format | 2026-04-08 |
| [BEMRosetta Tool](entities/bemrosetta-tool.md) | CLI mesh conversion tool wrapping Nemoh | 2026-04-08 |
| [CadQuery](entities/cadquery.md) | Python B-rep parametric CAD (OpenCASCADE, STEP) — candidate for digitalmodel / CAD-DEVELOPMENTS | 2026-04-17 |
| [Claude Code](entities/claude-code.md) | Anthropic CLI — default orchestrator for all workspace-hub work | 2026-04-08 |
| [Codex CLI](entities/codex-cli.md) | OpenAI CLI — default adversarial reviewer | 2026-04-08 |
| [Compliance Dashboard](entities/compliance-dashboard.md) | Automated review compliance tracking from commit history | 2026-04-08 |
| [Diffraction Analysis System](entities/diffraction-analysis-system.md) | Unified AQWA/OrcaWave/BEMRosetta diffraction workflow and schemas | 2026-04-09 |
| [digitalmodel](entities/digitalmodel.md) | Core engineering Python repo — 30 packages, 1587 files, 2085 classes | 2026-04-08 |
| [Elba Island LNG Mooring Incident](entities/elba-island-mooring-incident.md) | 2006 passing-vessel wake breakaway — $35M remediation | 2026-04-09 |
| [Gemini CLI](entities/gemini-cli.md) | Google CLI — optional third reviewer for complex work | 2026-04-08 |
| [GSD Framework](entities/gsd-framework.md) | "Get Stuff Done" workflow framework — sole workflow since 2026-03-25 | 2026-04-08 |
| [Hermes](entities/hermes.md) | Multi-agent orchestration framework (v0.4.0) | 2026-04-08 |
| [HMPE Mooring Line Failures](entities/hmpe-mooring-failures.md) | 2007-2011 industry-wide HMPE failures — ACF, jacketed rope, snap-back | 2026-04-09 |
| [LLM Wiki Tool](entities/llm-wiki-tool.md) | CLI for building persistent LLM knowledge bases (Karpathy pattern) | 2026-04-08 |
| [Mooring Analysis System](entities/mooring-analysis-system.md) | Station-keeping design — catenary, CALM/SALM, tension, fatigue, anchors | 2026-04-09 |
| [Naval Architecture Skill](entities/naval-architecture-skill.md) | Physics causal chain — hydrostatics, stability, seakeeping, roll damping | 2026-04-09 |
| [NW Shelf LNG Mooring Investigation](entities/nws-lng-mooring-investigation.md) | Woodside multi-year investigation — 50mm swell parting mooring lines | 2026-04-09 |
| [OpenFOAM CFD](entities/openfoam-cfd.md) | Open-source CFD toolkit — case setup, execution, diagnosis, validation | 2026-04-09 |
| [OrcaFlex Solver](entities/orcaflex-solver.md) | Orcina OrcaFlex marine dynamics — OrcFxAPI patterns and unit traps | 2026-04-08 |
| [OrcaWave Solver](entities/orcawave-solver.md) | Orcina diffraction/radiation solver — QTF, multi-body, OrcaFlex export | 2026-04-09 |
| [Prelude FLNG Mooring Failures](entities/prelude-flng-mooring.md) | Shell Prelude FLNG — nylon rope incompatibility, 16-line systemic failure | 2026-04-09 |
| [Skills System](entities/skills-system.md) | Primary knowledge carrier — 691+ git-tracked skill definitions | 2026-04-08 |
| [Solver Queue](entities/solver-queue.md) | Git-based async job dispatch for OrcaFlex/OrcaWave on licensed machines | 2026-04-08 |

## Sources (13 pages)

| Page | Description | Type | Ingested |
|------|-------------|------|----------|
| [Compound Engineering Methodology](sources/compound-engineering-methodology.md) | 5 operational lessons from running AI-augmented engineering | methodology-doc | 2026-04-08 |
| [AI Agent Guidelines](sources/ai-agent-guidelines-doc.md) | Cross-review policy and agent coordination rules | module-doc | 2026-04-08 |
| [Agent Equivalence Architecture](sources/agent-equivalence-architecture-doc.md) | Workflow-equivalent behavior across Claude/Codex/Gemini | module-doc | 2026-04-08 |
| [Baseline Testing Standards](sources/baseline-testing-standards-doc.md) | Universal TDD and pytest standards | module-doc | 2026-04-08 |
| [AI Development Ecosystem](sources/ai-development-ecosystem-doc.md) | Full-stack AI development ecosystem overview | module-doc | 2026-04-08 |
| [Career Learnings Seed](sources/career-learnings-seed.md) | 11 entries of career expertise across 23 years | knowledge-seed | 2026-04-08 |
| [Dark Intelligence Extractions](sources/dark-intelligence-extractions.md) | Legacy calculation extraction — 6 xlsx-poc + 1 geotechnical | dark-intelligence | 2026-04-08 |
| [Methodology Docs](sources/methodology-docs.md) | 6 methodology docs capturing ACE Engineer operations | methodology-doc | 2026-04-08 |
| [Skills Metadata](sources/skills-metadata.md) | 96 engineering skill files — marine-offshore, CFD, CAD, standards | skills-metadata | 2026-04-09 |
| [Mooring Failures LNG Terminals Seed](sources/mooring-failures-seed.md) | 40 entries — incidents, investigations, standards at LNG terminals | knowledge-seed | 2026-04-09 |
| [Closed Engineering Issues](sources/closed-engineering-issues.md) | Key decisions from 5 closed cat:engineering GitHub issues | closed-issues | 2026-04-09 |
| [Nightly Research Outputs](sources/research-outputs.md) | Standards tracking from nightly researcher system | research-outputs | 2026-04-09 |
| [HN CadQuery Discussion](sources/2026-04-17-hn-cadquery.md) | 180-point HN thread — CadQuery Python parametric CAD, B-rep vs mesh, LLM codegen signals | hn-discussion | 2026-04-17 |
| [Elements QGIS Flowline/DEM Deep Extraction](sources/elements-qgis-flowline-dem-deep-extraction.md) | First-pass extraction of Elements QGIS flowline alignment, UTM Zone 15N projection, DEM grid stats, and DXF entity counts | elements-deep-extraction | 2026-04-28 |

## Standards (8 pages)

| Page | Summary | Last Updated |
|------|---------|-------------|
| [API 579-1/ASME FFS-1](standards/api-579-ffs.md) | Fitness-for-Service — Levels 1-3 assessment | 2026-04-08 |
| [DNV-OS-E301](standards/dnv-os-e301.md) | Position mooring — infragravity waves, nearshore gap, OTG-18 | 2026-04-09 |
| [DNV-RP-C203](standards/dnv-rp-c203.md) | Fatigue design of offshore structures — S-N curves, DFF | 2026-04-08 |
| [DNV-RP-C205](standards/dnv-rp-c205.md) | Environmental conditions and loads — Morison, diffraction | 2026-04-08 |
| [DNV-RP-F101](standards/dnv-rp-f101.md) | Corroded pipeline assessment — Part A/B | 2026-04-08 |
| [DNV-RP-F105](standards/dnv-rp-f105.md) | Free spanning pipelines — VIV screening, fatigue, clean-room implementation | 2026-04-09 |
| [OCIMF MEG4](standards/ocimf-meg4.md) | Mooring equipment guidelines — HMPE, snap-back zones, mooring deck safety | 2026-04-09 |
| [OCIMF Tandem Mooring](standards/ocimf-tandem-mooring.md) | First-edition 2009 — tandem mooring & offloading at F(P)SO facilities | 2026-05-02 |

## Workflows (4 pages)

| Page | Summary | Last Updated |
|------|---------|-------------|
| [OrcaWave / OrcaFlex Fixture Expansion Cookbook](workflows/orcawave-orcaflex-fixture-expansion-cookbook.md) | Procedure for adding new structure-family semantic-proof fixtures without overfitting to native YAML formatting | 2026-04-26 |
| [OrcaWave-to-OrcaFlex Pipeline](workflows/orcawave-to-orcaflex-pipeline.md) | Automated single-command diffraction-to-vessel-type handoff | 2026-04-26 |
| [Parametric Engineering Reports](workflows/parametric-engineering-reports.md) | Automated parametric report generation for GTM demos | 2026-04-08 |
| [Solver Debugging Protocol](workflows/solver-debugging-protocol.md) | Systematic approach to debugging engineering solver failures | 2026-04-08 |
| [QGIS Flowline Alignment and DEM Preprocessing](workflows/qgis-flowline-dem-preprocessing.md) | Convert DXF flowline alignment plus UTM DEM grid into station/elevation engineering preprocessing artifacts | 2026-04-28 |

## Comparisons

_No query outputs filed yet._

| [[Elements ingest catalog — digitalmodel-qgis]](sources/elements-digitalmodel-qgis.md) | QGIS reusable engineering workflow/tooling data from the Elements drive. | 2026-04-28 |
| [[Elements ingest catalog — doris-university]](sources/elements-doris-university.md) | Doris University training corpus from the Elements drive; metadata-first training/source catalog. | 2026-04-28 |

| [Doris University Module 1.00 — Subsea Production Systems Overview](sources/doris-university-module-1-00-subsea-production-systems-overview.md) | Rows 1; metadata-first overview of SPS curriculum context. | 2026-04-29 |
| [Doris University Module 1.01 — Production Control Systems](sources/doris-university-module-1-01-production-control-systems.md) | Rows 2-3; metadata-first pointer to control-system curriculum materials. | 2026-04-29 |
| [Doris University Module 1.02 — Umbilical Systems](sources/doris-university-module-1-02-umbilical-systems.md) | Rows 4-6; metadata-first pointer to umbilical systems training materials. | 2026-04-29 |
| [Doris University Module 1.03 — Installation/Workover Control](sources/doris-university-module-1-03-installation-workover-control.md) | Rows 7-8; metadata-first pointer to IWOCS training materials. | 2026-04-29 |
| [Doris University Lunch and Learn — Control Systems](sources/doris-university-lunch-and-learn-control-systems.md) | Rows 13-14; metadata-first pointer to Doris-authored lunch-and-learn content. | 2026-04-29 |
| [Doris University Lunch and Learn — Umbilical Systems](sources/doris-university-lunch-and-learn-umbilical-systems.md) | Rows 15-17; metadata-first pointer to umbilical lunch-and-learn content. | 2026-04-29 |
| [Doris University syllabus snapshot](sources/doris-university-syllabus-snapshot.md) | Row 18; syllabus/taxonomy validation pointer. | 2026-04-29 |
| [Subsea production system overview](concepts/subsea-production-system-overview.md) | Connects Doris University SPS overview material to reusable subsea production system concepts. | 2026-04-29 |
| [Subsea production control system](concepts/subsea-production-control-system.md) | Metadata-first synthesis hook for production control system curriculum. | 2026-04-29 |
| [Subsea umbilical system](concepts/subsea-umbilical-system.md) | Metadata-first synthesis hook for umbilical system curriculum. | 2026-04-29 |
| [Installation/workover control system](concepts/installation-workover-control-system.md) | Metadata-first synthesis hook for IWOCS curriculum. | 2026-04-29 |
| [Methanol injection analysis](concepts/methanol-injection-analysis.md) | Calculation concept placeholder; no formulas or standard-derived text extracted. | 2026-04-29 |
| [Umbilical tube sizing and API 17E citation boundary](concepts/umbilical-tube-sizing-api-17e.md) | Calculation concept placeholder linked to API 17E public metadata stub. | 2026-04-29 |
| [Hydrostatic pressure with depth](concepts/hydrostatic-pressure-depth.md) | Calculation concept placeholder; no formula extraction in tranche 1. | 2026-04-29 |
| [Subsea accumulator sizing](concepts/subsea-accumulator-sizing.md) | Calculation concept placeholder; API 17G/API 16D resolution deferred until public metadata verified. | 2026-04-29 |