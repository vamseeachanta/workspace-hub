# Ecosystem 15-Day Sprint — Data Completeness + Calculation Coverage

> **WRK-1179** | Created: 2026-03-13 | Status: Design
> **Sprint window:** March 14–28, 2026 (15 days)

---

## 1. Context

The workspace-hub ecosystem has a mature strategic foundation (VISION.md, agent-vision.md,
roadmap-2026-h1.md) but gaps remain in two foundational areas:

- **Data:** The 1M-record doc index has partial content extraction; not all public O&G
  data sources are ingested; no vision doc for data-driven analysis exists
- **Calculations:** Engineering modules exist across 4 public repos but coverage is
  incomplete; no systematic gap map ties standards to implementations; no calculations
  vision doc exists

This sprint closes both gaps in parallel.

## 2. Scope

### In Scope

- Document index content extraction maximization (1M records)
- Public O&G data source research, catalog, and ingestion
- Calculation gap analysis across 4 repos (digitalmodel, worldenergydata, assethold, assetutilities)
- Implementation of highest-value calculations
- WRK item creation for all remaining gaps
- Two vision documents (data + calculations)

### Out of Scope

- Agent API layer / `ace.calc()` dispatcher (Q3 2026)
- aceengineer-website content generation
- Cross-repo workflow execution (Patterns 1–4)
- Nightly self-improving loop (WRK-234)
- OGManufacturing (client data — not a development target)

### Repo Boundaries

Development in 4 public repos only:

| Repo | Role in Sprint |
|------|---------------|
| workspace-hub | Doc index scripts (`scripts/data/document-index/`), specs, WRK items |
| digitalmodel | Calculation implementations + calculations vision doc |
| worldenergydata | Data source ingestion + data vision doc |
| assethold | Financial calculation implementations (VaR, Sharpe, etc.) |
| assetutilities | Shared constants + unit conversions needed by above |

Drilling and surveillance calculations belong in digitalmodel, not OGManufacturing.

## 3. Architecture — Two Parallel Streams

### Stream A: Data Completeness

**Owner:** worldenergydata + workspace-hub doc index
**Primary files:** `scripts/data/document-index/`, `worldenergydata/src/`

#### Phase 1 — Audit & Research (Days 1–3)

- Analyze `index.jsonl` (1M records): what % have content extraction (Phase B)
  vs. just filesystem metadata (Phase A)?
- Audit worldenergydata: which public sources are ingested, coverage, freshness
- Research all public O&G data sources globally — government, regulatory, academic,
  open-data portals. Classify each as:
  - **Already ingested** (e.g., BSEE, EIA, SODIR)
  - **Known but not yet ingested** (e.g., ERA5, NOAA NDBC)
  - **Newly discovered** (research output — BOEM, USGS, OPEC, IHS public, UN Comtrade, etc.)
- Output: `data-audit-report.md` with gap table

#### Phase 2 — Extract & Ingest (Days 4–10)

- Maximize content extraction from unprocessed docs (formulas, tables, design
  parameters, standard clauses)
- Ingest highest-value missing public O&G data sources into worldenergydata
- Each new source gets: loader module, tests, data schema

#### Phase 3 — Capture & Vision (Days 11–15)

- Every remaining doc extraction task → WRK item (child of WRK-1179)
- Every unintegrated data source → WRK item with priority + estimated effort
- Write `worldenergydata/docs/vision/DATA-VISION.md`:
  - What data the ecosystem has today
  - What data it needs for each workflow pattern (from agent-vision.md)
  - Roadmap: which sources unlock which engineering capabilities
  - How data feeds into the Sense → Plan → Act loop

### Stream B: Calculation Coverage

**Owner:** digitalmodel + assethold + assetutilities
**Primary files:** `digitalmodel/src/`, `assethold/src/`, `assetutilities/src/`, `specs/capability-map/`

#### Phase 1 — Audit & Gap Map (Days 1–3)

- Scan all 4 repos for existing calculation modules — catalog each with:
  function signature, standard referenced, inputs/outputs, test coverage
- Cross-reference against:
  - Standards in the doc index (methodology docs we own but haven't coded)
  - Industry-standard O&G calculations a consultancy should offer
  - Existing gap lists in `specs/architecture/agent-vision.md` (WRK-383/384)
- For each gap: capture design data needed (standard, equations, inputs) and
  analysis methodology (how the calculation fits into a workflow)
- Output: updated `specs/capability-map/<repo>.yaml` for all 4 repos

#### Phase 2 — Implement (Days 4–12)

- Priority order: calculations **closest to complete** (partial implementations,
  standard doc available, test data exists) get done first — maximize throughput
- Each calculation follows TDD: test with worked example from standard → implement → validate
- Target repos in parallel:
  - **digitalmodel:** structural, subsea, hydrodynamics, CP, drilling gaps
  - **worldenergydata:** Arps decline curves, cross-source synthesis
  - **assethold:** VaR/CVaR, GICS classification, Sharpe/Sortino
  - **assetutilities:** shared constants, unit conversions needed by the above

**Calculation report standard (mandatory):** Every new calculation MUST follow the
`calculation-report` skill (`.claude/skills/data/calculation-report/SKILL.md`).
Each implementation produces:

- A `calculation.yaml` with: metadata, inputs (name/symbol/value/unit), methodology
  (standard reference + LaTeX equations), outputs (with pass/fail limits), assumptions,
  references
- Validated against `config/reporting/calculation-report-schema.yaml`
- Renderable via `scripts/reporting/generate-calc-report.py`
- At least one worked example YAML in `examples/reporting/`

#### Phase 3 — Capture & Vision (Days 13–15)

- Every unimplemented calculation → WRK item with: standard reference, target module,
  acceptance criteria, design data pointers
- Run WRK-386 gap-to-WRK generator if operational, or manually create items
- Write `digitalmodel/docs/vision/CALCULATIONS-VISION.md`:
  - Current calculation coverage by discipline
  - Gap register: what's missing and why it matters
  - Tier progression: how each gap closure moves the repo from Tier 1 → Tier 2
  - Priority framework: which calculations unlock which workflow patterns

## 4. Coordination & Execution

### Parallel Execution

- Stream A and Stream B run simultaneously via separate agent sessions
- Stream A works in: `scripts/data/document-index/`, `worldenergydata/`
- Stream B works in: `digitalmodel/`, `assethold/`, `assetutilities/`, `specs/capability-map/`
- Overlap point: `assetutilities` (shared constants) — Stream B owns; Stream A consumes
- **Conflict rule:** assetutilities changes must not break existing public APIs; additions only during the sprint. If a breaking change is needed, coordinate at the Day 10 checkpoint before merging.

### Checkpoints

- **Day 3:** Audit outputs reviewed — redirect if needed
- **Day 10:** Progress check — are we on track for Phase 3?
- **Day 15:** Final deliverables reviewed

### WRK Integration

- WRK-1179 is a **Feature WRK** with two child streams
- Child WRKs generated during Phase 3 feed into the main work queue
- Existing related WRKs (309, 383, 384, 386, 317, 318) get linked or closed as appropriate

## 5. Success Criteria

| Metric | Stream A (Data) | Stream B (Calculations) |
|--------|----------------|------------------------|
| Audit complete | Doc index gap report + public data source catalog | Calculation gap map across 4 repos |
| Work done | Max content extracted; new sources ingested | Max calculations implemented (TDD + calc-report YAML) |
| Gaps captured | All remaining docs/sources → WRK items | All remaining calcs → WRK items |
| Vision written | `worldenergydata/docs/vision/DATA-VISION.md` | `digitalmodel/docs/vision/CALCULATIONS-VISION.md` |

## 6. Related Work

| WRK | Title | Relationship |
|-----|-------|-------------|
| WRK-309 | Document intelligence | Stream A builds on Phase A–E work |
| WRK-383 | Standards capability map | Stream B produces/updates this |
| WRK-384 | Module registry | Stream B audit feeds this |
| WRK-386 | Gap-to-WRK generator | Stream B Phase 3 uses this |
| WRK-317 | Plotly Dash dashboard | Stream A may advance this |
| WRK-318 | Arps decline curves | Stream B implements this |
| WRK-319 | Real-time EIA feed | Stream A may advance this |
| WRK-321 | Carbon cost sensitivity | Stream B may implement this |

---

*Design approved: 2026-03-13 | WRK-1179*
