# Superintelligent Engineering Agent Architecture Blueprint

> WRK-385 | Created: 2026-02-24 | Status: Canonical

---

## Table of Contents

1. [Vision](#part-1--vision)
2. [Capability Tiers](#part-2--capability-tiers-per-repo)
3. [Repo Roles](#part-3--repo-roles)
4. [Knowledge → Capability → Action Loop](#part-4--knowledge--capability--action-loop)
5. [Cross-Repo Workflow Patterns](#part-5--cross-repo-workflow-patterns)
6. [Milestones](#part-6--milestones)

---

## Part 1 — Vision

### What "Superintelligent Engineering Agent" Means Here

The phrase is specific, not aspirational. In this context it means:

> A software agent capable of receiving an engineering problem statement in natural or
> structured language, autonomously selecting the applicable codes and standards, invoking
> the correct calculation modules, validating results against code limits, and producing a
> complete, traceable engineering deliverable — without step-by-step human instruction.

The word "superintelligent" does not mean sentient or general-purpose. It means the agent
has access to more standards knowledge, more calculation history, and more cross-discipline
integration than any individual engineer could hold in working memory. The agent compounds
that knowledge across every session, every standard implemented, every gap filled.

### End State

The end state is a collection of agents, one per engineering discipline and one per data
domain, that together can:

1. **Read standards** — ingest structured references to the 623K+ classified documents
   catalogued in WRK-309 Phase B and resolve them to specific calculation clauses.

2. **Perform calculations** — dispatch to the correct module in digitalmodel or its
   peer repos, passing validated inputs and receiving structured outputs.

3. **Validate against code** — compare outputs to pass/fail criteria defined in the
   applicable standard, produce a pass/fail report with reference to the clause checked.

4. **Produce deliverables** — assemble individual calculation results into a complete
   calculation package: cover sheet, design basis, calculation sheets, results tables,
   and code check summary — in a format suitable for engineering review or stamping.

5. **Identify gaps and spawn work** — when a required standard is not yet implemented,
   emit a structured WRK item (via WRK-386) rather than failing silently or producing
   an incorrect result.

6. **Compose across repos** — a single agent query can orchestrate worldenergydata for
   metocean and production data, digitalmodel for the engineering calculations, and
   assethold for the financial screening, returning an integrated result.

### Why This Architecture Matters

The WRK-309 document intelligence programme produced a classified index of thousands of
engineering standards, codes, reports, and reference papers stored across the workspace
drives. Phase B extracted summaries. Phase C mapped documents to repos.

That work is only valuable if the documents drive capability. Without a structured
capability architecture, the document index remains metadata — useful for retrieval but
not for action. With this architecture, every document in the index has a path to
implementation:

```
Document exists in index
    → mapped to a specific module (WRK-383)
    → module registry records current status (WRK-384)
    → if gap: WRK item auto-generated (WRK-386)
    → WRK item implemented
    → module capability advances one tier
```

At scale, with 50-200 targeted WRK items covering unimplemented standards across all
tier-1 repos, the compounding effect is significant. Each standard implemented makes
the next calculation possible. Each module reaching Tier 2 unlocks a new class of
engineering queries. Each cross-repo workflow pattern defines a repeatable capability
available to every future project.

This document is the canonical blueprint that every future WRK item should reference.
A WRK item that cannot explain how it advances a repo toward its tier target is either
misdirected or needs to be split.

---

## Part 2 — Capability Tiers (per repo)

Three tiers define the progression from a code library to an autonomous engineering agent.
The tiers are cumulative: Tier 2 requires Tier 1 to be solid; Tier 3 requires Tier 2.

---

### Tier 1 — Engineering Calculator

**Definition**: A module that accepts structured inputs, applies a deterministic algorithm
derived from a specific engineering standard, and returns structured outputs.

**Characteristics**:
- Inputs and outputs are typed and documented
- The calculation is traceable to a specific standard clause
- The module is covered by unit tests with at least one worked example from the standard
- Results are reproducible: same inputs always produce same outputs
- No natural language processing; no module selection logic
- No report generation

**Example** (digitalmodel):
```python
from digitalmodel.structural.fatigue import calculate_damage

result = calculate_damage(
    stress_range=[50.0, 40.0, 30.0],  # MPa
    cycle_count=[1e5, 2e5, 5e5],
    sn_curve="D",                      # DNVGL-RP-C203 Table 2-1
    environment="seawater_cp"          # cathodic protection
)
# result.damage = 0.73  (< 1.0 → pass)
# result.standard = "DNVGL-RP-C203"
# result.clause = "Sec 2.4"
```

**Measurement** (what "Tier 1 for a module" means):
- Module exists in source
- At least one standard is explicitly referenced in code or docstring
- At least one test passes with a known result from the standard
- Inputs and outputs are documented

**Current state**: Most digitalmodel modules are Tier 1 for their primary standard.
worldenergydata data-fetch modules are Tier 1. assethold calculation modules are Tier 1.

---

### Tier 2 — Engineering Assistant

**Definition**: An agent layer on top of Tier 1 modules that accepts a natural language or
semi-structured engineering problem, selects the correct modules and sequences them,
validates outputs against code limits, and produces a structured calculation report.

**Characteristics**:
- Accepts natural language or template-structured input (problem statement)
- Selects applicable standards from the module registry
- Composes multiple Tier 1 modules into a calculation sequence
- Validates each result against code pass/fail criteria
- Produces a machine-readable and human-readable calculation report
- Handles missing inputs by prompting for them or applying conservative defaults
- Emits a WRK item if a required module is not implemented (gap detection)

**Example** (digitalmodel Tier 2 target):
```
User: "Check fatigue life of tubular joint T1 using JONSWAP scatter at 120m water depth,
       cathodic protection, DNV-RP-C203."

Agent:
  1. Reads problem → identifies: fatigue assessment, tubular joint, DNV-RP-C203
  2. Queries module registry → selects: structural/fatigue, hydrodynamics/wave_spectra
  3. Checks inputs: needs SCF geometry parameters → prompts user for Efthymiou inputs
  4. Runs wave_spectra.jonswap() → stress transfer function → cycle histogram
  5. Runs fatigue.calculate_damage(cycles, sn_curve="T") → D = 0.73
  6. Validates: D < 1.0 → PASS per DNV-RP-C203 Sec 2.4
  7. Produces: calc sheet with inputs, method, result, code reference, pass/fail verdict
```

**Measurement** (what "Tier 2 for a module" means):
- Module registry entry exists (WRK-384)
- Agent API endpoint wraps the Tier 1 module
- Natural language problem mapper can route to the module
- Calculation report template produces structured output
- Gap detection emits a WRK item when the module cannot satisfy the request

**Target**: digitalmodel and worldenergydata by end 2026.

---

### Tier 3 — Autonomous Engineering Agent

**Definition**: A project-level agent that receives a high-level brief, autonomously
determines the applicable standards and design methodology, iterates the design until all
code checks pass, and produces a complete stamped calculation package.

**Characteristics**:
- Input: project brief (asset type, water depth, metocean regime, regulatory jurisdiction)
- Autonomous standards selection: queries the capability map (WRK-383) to identify all
  applicable codes for the project type
- Iterative design: varies parameters until all code checks pass
- Cross-repo orchestration: composes Tier 2 agents from multiple repos
- Gap identification: if a required standard is not implemented, creates a WRK item and
  documents the gap in the calculation package with a conservative fallback
- Deliverable assembly: produces a complete calculation package with:
  - Design basis document
  - Applied standards list
  - Individual calculation sheets (one per module)
  - Code check summary table
  - Gap register (what was not checked and why)
- Human review hook: pauses for engineer review at configurable checkpoints

**Example** (workspace-hub Tier 3):
```
User: "Assess feasibility of a 12" rigid pipeline at 1500m water depth in the GOM.
       Regulatory: BSEE. Operator: independent. Timeline: pre-FEED."

Agent:
  1. Identifies applicable standards (GOM, rigid pipeline, 1500m, BSEE):
     DNV-ST-F101, API RP 1111, DNVGL-RP-C205, BSEE 30 CFR 250
  2. Queries worldenergydata → GOM metocean (ERA5 + NDBC) → 100yr Hs, Tp, current
  3. Dispatches to digitalmodel:
     - pipeline.wall_thickness(OD=12in, MAOP=5000psi, material="X65")
     - pipeline.collapse_check(water_depth=1500m, wall_thickness=...)
     - pipeline.catenary_riser(...)
  4. Validates all checks → wall_thickness governed by collapse, not MAOP
  5. Iterates wall_thickness upward until collapse check passes
  6. Detects gap: on-bottom stability module not implemented → emits WRK item
  7. Assembles: pre-FEED feasibility calculation package
  8. Pauses: "Review requested before finalising — gap: on-bottom stability not checked"
```

**Measurement** (what "Tier 3 for a repo" means):
- workspace-hub can orchestrate agents in two or more repos with a single workflow spec
- A project brief produces a calculation package without step-by-step human instruction
- Gap detection and WRK generation is automatic
- Human review hooks are configurable

**Target**: workspace-hub by end 2027.

---

## Part 3 — Repo Roles

| Repo | Current State | Tier Target | Key Gaps |
|------|---------------|-------------|----------|
| digitalmodel | 700+ modules, Tier 1 for most | Tier 2 by end 2026 | No agent API layer; no standards traceability at function level; spectral fatigue incomplete; no CP module |
| worldenergydata | Data aggregation, Tier 1 data fetch | Tier 2 synthesis by end 2026 | No cross-source synthesis layer; no unified query API; no production forecasting module |
| assetutilities | Utility functions, supporting | Shared infra for Tier 2+ | Not wired into other repos as a shared dependency; constants duplicated across repos |
| workspace-hub | Orchestration and WRK management | Tier 3 coordinator by end 2027 | No workflow specs; no agent composition layer; no unified CLI (WRK-326) |

---

### digitalmodel — Engineering Calculation Engine

**Current state**: Tier 1 for most of its 700+ modules across structural, subsea,
hydrodynamics, marine_ops, and asset_integrity disciplines. The modules are tested,
documented (partially), and used in production engineering work. However:

- Standards are referenced informally in comments or not at all — no machine-readable
  traceability from function to standard clause
- No agent API layer: callers must know module paths and input schemas
- No module registry: agents cannot discover what digitalmodel can do
- Spectral fatigue is incomplete (time-domain and frequency-domain partial)
- No cathodic protection module (DNV-RP-B401 gap — anode design not implemented)
- On-bottom stability not implemented (DNV-RP-F109 gap)
- No agent-native report generation

**Tier 2 target requirements**:
1. Module registry complete (WRK-384): every module documented with capabilities, standards,
   inputs, outputs, maturity, and gaps
2. Standards capability map complete (WRK-383): every standard in the library mapped to the
   module that implements it (or the gap if not implemented)
3. Agent API layer: `ace.calc(module_id, inputs)` dispatcher callable from workspace-hub
4. Calculation report template: structured output per calculation
5. Natural language problem mapper: routes engineering queries to modules
6. Gap-to-WRK emission: when a module cannot satisfy a request, a WRK item is created

**Key WRK references**: WRK-383, WRK-384, WRK-386, WRK-311 (fatigue), WRK-326 (CLI)

---

### worldenergydata — Market and Field Intelligence Agent

**Current state**: Tier 1 for data acquisition. BSEE, EIA, SODIR, and metocean modules
fetch and store data correctly. CLI tools are mature. However:

- Data sources are queried independently — no cross-source synthesis
- No production forecasting module (decline curves not implemented: WRK-318)
- No unified query API: callers must know which source to query
- No field development screening capability (multi-source correlation not possible)
- Dashboard not yet built (WRK-317)
- EIA real-time feed not wired (WRK-319)
- Field development economics carbon sensitivity not implemented (WRK-321)

**Tier 2 target requirements**:
1. Cross-source synthesis layer: unified query API across BSEE + EIA + SODIR + metocean
2. Production forecasting module: Arps decline curves (WRK-318)
3. Field development screening: correlate production data + metocean + regulatory data
   to identify candidate fields for development scenarios
4. Structured output format: query results return typed, validated data structures
5. Agent interface: worldenergydata callable from workspace-hub agent workflows

**Key WRK references**: WRK-317, WRK-318, WRK-319, WRK-320, WRK-321

---

### assetutilities — Shared Infrastructure Agent

**Current state**: Utility functions for common engineering tasks: unit conversions,
calculations, data IO, common patterns. Early-stage but functional for current users.

**Role in the agent architecture**: Not a domain-specific agent. assetutilities provides
shared infrastructure that Tier 2+ agents depend on:

- Common unit conversion (not to be duplicated in each repo)
- Shared material and engineering constants (WRK-327)
- Standard IO patterns for calculation report assembly
- Data pipeline adapters

**Gap**: Currently not installed as a dependency by digitalmodel or worldenergydata.
Constants and conversion functions are duplicated. Centralising via WRK-327 is a
prerequisite for reliable cross-repo calculation consistency.

**Tier target**: Tier 1 (shared infrastructure), but enabler of Tier 2 in other repos.

**Key WRK references**: WRK-327

---

### workspace-hub — Orchestration and Vision Layer

**Current state**: Orchestrates the WRK queue, maintains ecosystem configuration,
provides skills and automation for managing the workspace. Has no engineering calculation
capability of its own. Has no workflow composition layer. Tier 0 as an engineering agent.

**Role in the agent architecture**: The Tier 3 coordinator. workspace-hub does not perform
calculations — it orchestrates agents that do. Its Tier 3 capability is defined by:

1. Workflow specs (`specs/architecture/workflow-patterns.yaml`) that describe multi-repo
   engineering workflows at a level an agent can execute
2. A composition layer that dispatches sub-tasks to the correct repo agents
3. Standards capability map (WRK-383) maintained at the hub level — queryable by any agent
4. Gap-to-WRK generator (WRK-386) that closes the knowledge-to-action loop
5. Unified CLI (WRK-326) that exposes all repo tools under a single `ace` entry point

**Tier 3 target requirements**:
1. At least four canonical workflow patterns specified and executable
2. Cross-repo dispatch: workspace-hub can invoke digitalmodel + worldenergydata in sequence
3. Project brief → calculation package: end-to-end without step-by-step prompting
4. Gap register: automatically tracks what was not checked in any given project run
5. WRK generation: gaps automatically become work items

**Key WRK references**: WRK-383, WRK-385 (this WRK), WRK-386, WRK-326

---

## Part 4 — Knowledge → Capability → Action Loop

The architecture is a closed loop. Knowledge drives capability. Capability drives action.
Action fills gaps. Gaps become new knowledge. The loop runs continuously.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     KNOWLEDGE (WRK-309)                                     │
│                                                                             │
│  623K+ classified documents on /mnt/ace, /mnt/dde                          │
│  Phase A: filesystem index (path, size, mtime, host)                        │
│  Phase B: content extracted — title, summary, keywords, discipline          │
│  Phase C: domain classification — doc → repo → discipline                   │
│  Phase D: data source YAML — doc → standard ID → repo                      │
│  Phase E: linked registry — queryable by domain, standard, repo             │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   STANDARD → MODULE MAPPING (WRK-383)                       │
│                                                                             │
│  For each standard in the registry:                                         │
│    standard ID → repo → specific module                                     │
│    status: implemented | partial | gap                                      │
│                                                                             │
│  Output: specs/capability-map/<repo>.yaml                                   │
│  Scope: digitalmodel (40+ modules), worldenergydata, assetutilities         │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MODULE REGISTRY (WRK-384)                               │
│                                                                             │
│  For each module in the capability map:                                     │
│    module ID, description, maturity, capabilities                           │
│    standards[] with status per standard                                     │
│    inputs[], outputs[], gaps[]                                              │
│                                                                             │
│  Output: digitalmodel/specs/module-registry.yaml                           │
│  Enables: agent discovery, gap analysis at module granularity               │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   GAP-TO-WRK GENERATOR (WRK-386)                            │
│                                                                             │
│  For each status: gap entry in capability map:                              │
│    - standard doc exists in library (Phase B SHA confirmed)                 │
│    - specific module identified (WRK-383)                                   │
│    → generate WRK item: implement <STANDARD> in <MODULE>                    │
│                                                                             │
│  Output: .claude/work-queue/pending/WRK-NNN.md (50-200 items)              │
│  Template: standard metadata + module target + acceptance criteria          │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 IMPLEMENTATION WRK ITEMS                                    │
│                                                                             │
│  Each WRK item: implement <STANDARD-ID> in <REPO>/<MODULE>                 │
│  Format:                                                                    │
│    - Standard reference with SHA (immutable, auditable)                     │
│    - Target module and current status                                       │
│    - Acceptance criteria: unit tests + worked example validation            │
│    - Module registry updated on completion: gap → implemented               │
│                                                                             │
│  On completion: module registry updated → capability map updated →          │
│  loop completes → next gap identified                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Why This Loop Matters

Without the loop, WRK items are isolated. An engineer decides what to implement based
on current project need. Coverage is project-driven and reactive.

With the loop, the document index is the source of truth. Every standard in the library
that is not yet implemented becomes a WRK item. Priority is set by tier importance and
agent capability. The gap list is exhaustive, not ad-hoc. Coverage becomes systematic.

The loop also makes progress measurable. "What percentage of standards in the library are
implemented?" is a query against the capability map. "What are the highest-priority gaps?"
is a sort of the WRK queue by priority. "What has improved since last quarter?" is a diff
of the module registry.

---

## Part 5 — Cross-Repo Workflow Patterns

Four canonical workflow patterns define what a Tier 2/3 system can deliver today and
what it targets. Each pattern is a template for a class of engineering project, not a
single calculation.

Full machine-readable definitions are in `specs/architecture/workflow-patterns.yaml`.

---

### Pattern 1: Subsea Fatigue Assessment

**Use case**: Structural fatigue life assessment for an offshore steel structure
(jacket, topside node, riser, mooring line) under stochastic wave loading.

**Repos involved**: digitalmodel

**Disciplines**: structural/fatigue, hydrodynamics/wave_spectra, subsea/mooring_analysis

**Workflow**:
```
1. Input: structure geometry, joint classification, water depth, site metocean
2. digitalmodel/hydrodynamics/wave_spectra:
   - Construct JONSWAP scatter matrix from Hs/Tp data
   - Apply directional spreading
3. digitalmodel/structural/fatigue:
   - Compute stress transfer function (RAO)
   - Apply Efthymiou SCF parametric equations
   - Run spectral fatigue: stress power spectral density → cycle histogram
   - Calculate Palmgren-Miner accumulated damage per S-N curve
4. Validate: D < 1.0 (or D < DFF limit) → pass/fail per DNV-RP-C203
5. Output: fatigue calculation sheet with scatter matrix, SCFs, S-N curves, damage
```

**Standards applied**: DNVGL-RP-C203 (primary), DNVGL-RP-C205 (wave spectra),
ISO 19902 (structural), API RP 2SK (mooring)

**Current gaps**: Spectral fatigue partial (deterministic fatigue implemented);
cathodic protection correction factor not automated

**Deliverable**: Fatigue calculation package — scatter matrix, transfer functions,
damage table, code check summary

---

### Pattern 2: Deepwater Pipeline Feasibility

**Use case**: Pre-FEED feasibility assessment for a deepwater rigid pipeline system,
covering pressure containment, collapse, and riser configuration.

**Repos involved**: digitalmodel, worldenergydata

**Workflow**:
```
1. Input: water depth, pipe OD, MAOP, fluid type, regulatory regime, location
2. worldenergydata/metocean:
   - Query ERA5 or NDBC for 100yr Hs, Tp, current profile at site
3. digitalmodel/subsea/pipeline:
   - Wall thickness: pressure containment per DNV-ST-F101 Eq 5.6
   - Collapse check: external pressure capacity per DNV-ST-F101 Sec 5.4
   - Buckle propagation: DNV-ST-F101 Sec 5.4.5
4. digitalmodel/subsea/catenary_riser:
   - Static catenary configuration (touch-down point, top angle, dynamic offset)
   - Dynamic riser analysis: first-order wave-frequency response
5. digitalmodel/marine_ops/marine_engineering:
   - Installation window: weather criteria for lay barge operations
6. Validate all code checks → iterate wall_thickness if collapse governs
7. Output: pre-FEED pipeline calculation package
```

**Standards applied**: DNV-ST-F101 (pipeline), API RP 1111 (deepwater pipeline),
DNV-OS-F201 (dynamic risers), DNVGL-RP-C205 (environmental conditions),
BSEE 30 CFR 250 (GOM regulatory, if applicable)

**Current gaps**: On-bottom stability not implemented (DNV-RP-F109);
worldenergydata metocean query not yet wired to digitalmodel

**Deliverable**: Pre-FEED feasibility pack — wall thickness selection, collapse check,
riser configuration sketch, installation criteria

---

### Pattern 3: Field Development Screening

**Use case**: Rapid screening of candidate fields for development potential using
public regulatory and production data, without access to operator proprietary data.

**Repos involved**: worldenergydata

**Workflow**:
```
1. Input: geographic area, water depth range, target production threshold, timeline
2. worldenergydata/bsee:
   - Query BSEE production database for fields matching water depth + area criteria
   - Filter by production history (active, recently inactive, undeveloped leases)
3. worldenergydata/eia_us:
   - Overlay regional production trends (basin-level decline, price history)
4. worldenergydata/metocean:
   - Attach metocean summary (100yr Hs/Tp, current) for each candidate field location
5. worldenergydata/production:
   - Apply Arps decline curve to remaining reserves estimate
   - Calculate plateau rate, economic limit, recoverable reserves
6. worldenergydata/finance (or assethold):
   - Run NPV screening at configurable oil price and discount rate
   - Apply carbon cost sensitivity (WRK-321)
7. Rank candidates by NPV, reserves, metocean severity
8. Output: field screening report — ranked candidate list with key metrics
```

**Standards/sources applied**: BSEE production API, EIA API v2, SODIR API,
ERA5/NOAA metocean, Arps decline (SPE), BSEE 30 CFR 250 (regulatory constraints)

**Current gaps**: Arps decline not implemented (WRK-318); cross-source synthesis
layer not built; carbon cost sensitivity not built (WRK-321)

**Deliverable**: Screening report — ranked field candidates with reserves, metocean,
NPV sensitivity, and development risk flags

---

### Pattern 4: Portfolio Risk Analysis

**Use case**: Quantitative risk assessment for an energy stock portfolio, including
value-at-risk, factor exposure, and scenario analysis.

**Repos involved**: assethold

**Workflow**:
```
1. Input: portfolio holdings (ticker, quantity, cost basis), analysis date, lookback period
2. assethold/data:
   - Fetch historical price data (yfinance)
   - Attach fundamentals: P/E, P/B, EV/EBITDA (WRK-322)
3. assethold/risk:
   - Calculate daily returns for each holding
   - Compute portfolio covariance matrix
   - Value at Risk (VaR): parametric (1-day, 1-week, 95th/99th percentile)
   - Conditional VaR (CVaR / Expected Shortfall)
   - Sharpe ratio and Sortino ratio per position and portfolio
   - Maximum drawdown: peak-to-trough analysis per holding and portfolio
4. assethold/sector:
   - GICS sector classification for each holding (WRK-323)
   - Sector concentration: flag if >40% in a single sector
   - Energy sub-sector breakdown: upstream, midstream, downstream, services
5. assethold/options (if applicable):
   - Covered call analysis: premium/yield calculator (WRK-325)
6. Output: portfolio risk report — VaR, CVaR, Sharpe, sector exposure heatmap
```

**Standards/frameworks applied**: Modern Portfolio Theory (Markowitz), GICS sector
taxonomy, Black-Scholes for options (if applicable), MSCI risk factor model

**Current gaps**: VaR/CVaR/Sharpe not yet implemented (WRK-323); GICS classification
not automated (WRK-323); covered call analyser not built (WRK-325)

**Deliverable**: Portfolio risk dashboard — VaR summary, factor exposure table,
sector concentration chart, Sharpe/Sortino by position

---

## Part 6 — Milestones

Milestones are concrete, per-repo, per-tier, with WRK references. Dates are targets, not
commitments. The WRK queue is the authoritative source of current status.

---

### digitalmodel — Path to Tier 2 (target: end 2026)

#### Q1 2026 — Foundation
- [ ] **WRK-383**: Standards capability map complete
  - 40+ modules mapped to standards
  - Status: implemented | partial | gap for each
  - Output: `specs/capability-map/digitalmodel.yaml`

- [ ] **WRK-384**: Module registry complete
  - All modules listed with capabilities, inputs, outputs, maturity
  - Standards linked to capability map (SHA references)
  - Output: `digitalmodel/specs/module-registry.yaml`

#### Q2 2026 — Gap Fill (high-priority standards)
- [ ] **Auto-generated WRK items (WRK-386)**: 50+ gap items created
  - Each item: implement one standard in one module
  - Estimated: 15-20 items for structural, 10-15 for subsea, 5-10 for hydrodynamics

- [ ] **Key gaps (examples)**:
  - BS 7608 S-N curves (structural/fatigue)
  - DNV-RP-B401 cathodic protection (subsea CP module, new)
  - DNV-RP-F109 on-bottom stability (subsea/pipeline)
  - ISO 19902 jacket structural checks (structural/structural_analysis)
  - DNVGL-RP-C205 wave spectra (full spectral fatigue integration)

#### Q3 2026 — Agent API Layer
- [ ] Agent API dispatcher: `ace.calc(module_id, inputs)` — callable from workspace-hub
- [ ] Natural language problem mapper: routes engineering queries to module registry
- [ ] Calculation report template: structured output per calculation (JSON + PDF)
- [ ] Gap emission: if module cannot satisfy request, WRK item auto-created

#### Q4 2026 — Tier 2 Verification
- [ ] End-to-end fatigue assessment (Pattern 1) without step-by-step prompting
- [ ] End-to-end pipeline feasibility (Pattern 2, digitalmodel components)
- [ ] Module registry covers 100% of digitalmodel source modules
- [ ] 80%+ of identified standards gaps closed (measured against capability map)

---

### worldenergydata — Path to Tier 2 (target: end 2026)

#### Q1 2026 — Data Layer
- [ ] **WRK-317**: Plotly Dash dashboard — BSEE + FDAS interactive visualisation
- [ ] **WRK-318**: Arps decline curve module (exponential, hyperbolic, harmonic)
- [ ] **WRK-319**: Real-time EIA/IEA feed ingestion — weekly automated updates

#### Q2 2026 — Synthesis Layer
- [ ] **WRK-321**: Field development economics — MIRR/NPV with carbon cost sensitivity
- [ ] Cross-source synthesis API: unified query across BSEE + EIA + SODIR + metocean
- [ ] Structured output: typed, validated data structures for all sources

#### Q3 2026 — Agent Interface
- [ ] worldenergydata callable from workspace-hub agent workflows
- [ ] Field screening query: multi-source correlation with ranked output
- [ ] Structured report output: field screening report template

#### Q4 2026 — Tier 2 Verification
- [ ] End-to-end field screening (Pattern 3) without step-by-step prompting
- [ ] worldenergydata → digitalmodel data handoff working (Pipeline Pattern 2, step 2)

---

### assetutilities — Shared Infrastructure (target: stable Tier 1 by end 2026)

#### Q1-Q2 2026
- [ ] **WRK-327**: Shared engineering constants library
  - Steel material properties (API 5L grades, structural steel)
  - Seawater properties (density, viscosity vs temperature/salinity)
  - Unit conversion utilities (SI/Imperial)
  - Installed as `ace-constants` package, used by digitalmodel and worldenergydata

- [ ] Common IO patterns: shared data pipeline adapters for CSV/JSON/YAML
- [ ] Wired as a declared dependency in digitalmodel and worldenergydata pyproject.toml

---

### workspace-hub — Path to Tier 3 (target: end 2027)

#### Q1 2026 — Architecture and Mapping
- [ ] **WRK-385** (this WRK): Architecture blueprint committed
- [ ] **WRK-383**: Standards capability map at hub level (cross-repo view)
- [ ] **WRK-386**: Gap-to-WRK generator operational

#### Q2-Q3 2026 — CLI and Composition
- [ ] **WRK-326**: Unified `ace` CLI — single entry point routing to all repos
- [ ] Cross-repo dispatch layer: workspace-hub can invoke digitalmodel + worldenergydata
- [ ] Workflow spec executor: reads `workflow-patterns.yaml`, dispatches steps

#### Q4 2026 — Pattern Execution (Tier 2 orchestration)
- [ ] Pattern 1 (Subsea Fatigue) executable end-to-end from workspace-hub
- [ ] Pattern 2 (Pipeline Feasibility) executable end-to-end
- [ ] Pattern 3 (Field Screening) executable end-to-end

#### Q1-Q2 2027 — Project Brief → Deliverable (Tier 3)
- [ ] Project brief parser: extracts parameters (asset type, water depth, jurisdiction)
- [ ] Autonomous standards selection from capability map
- [ ] Gap register: automatic tracking of what was not checked
- [ ] Calculation package assembler: cover sheet + calc sheets + code check summary

#### Q3-Q4 2027 — Tier 3 Verification
- [ ] End-to-end pre-FEED assessment from project brief without step-by-step prompting
- [ ] Stamped calculation package produced with full audit trail
- [ ] Gap WRK items generated automatically during project run
- [ ] Pattern 4 (Portfolio Risk) integrated for investment screening

---

## Appendix — Architecture File Map

```
specs/architecture/
├── agent-vision.md          ← This document (WRK-385)
├── capability-tiers.yaml    ← Structured tier definitions per repo (WRK-385)
└── workflow-patterns.yaml   ← Canonical cross-repo workflow templates (WRK-385)

specs/capability-map/        ← Standard → module linkage (WRK-383)
├── digitalmodel.yaml
├── worldenergydata.yaml
└── assetutilities.yaml

digitalmodel/specs/
└── module-registry.yaml     ← Module-level metadata (WRK-384)

scripts/data/document-index/
└── phase-f-gap-wrk-generator.py  ← Gap → WRK automation (WRK-386)
```

---

*Last updated: 2026-02-24. Canonical reference: WRK-385.*
*Related: WRK-309 (document intelligence), WRK-383 (capability map), WRK-384 (module registry), WRK-386 (gap generator).*
