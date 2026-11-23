# Weekly Research Synthesis — 2026-04-03

## Action Table

| Finding | Impact | Action | Status |
|---------|--------|--------|--------|
| OrcaFlex 11.6 Python variable loads | High | Promote to PROJECT.md + Phase 7 research | Pending |
| SACS Cloud Services 10x speedup | High | GTM positioning strategy shift | Pending |
| Free/low-cost competitor calculators (SkyCiv, TheNavalArch) | High | Competitive feature audit + differentiation | Pending |
| DNV-RP-C203 2024 S-N curves (prior week carryover) | High | Create GitHub issue for module update | Pending |
| pandas 3.0 Copy-on-Write (prior week carryover) | High | Create GitHub issue for tier-1 audit | Pending |
| ASME B31.4-2025 (prior week carryover) | High | Create GitHub issue for clause verification | Pending |
| uv 0.11.0 TLS change (prior week carryover) | High | Create GitHub issue for 4-machine test | Pending |
| PyYAML SafeLoader audit (prior week carryover) | High | Create GitHub issue for security audit | Pending |
| ANSYS 2026 GPU acceleration | Medium | Evaluate GPU-aware refactor for Phase 7+ | Pending |
| Blue Kenue open-source mesh | Medium | Add Phase 999.6 backlog item | Pending |
| DNV July 2025/2026 hearing (prior week) | Medium | Monitor hearing outcome (closes 12 Apr) | Pending |
| ABS Offshore Rules consolidation (prior week) | Medium | Website copy audit | Pending |
| NumPy 2.4 expired deprecations (prior week) | Medium | Create GitHub issue for grep-and-fix | Pending |
| GSD-2 for Phase 5 automation (prior week) | Medium | Evaluate architecture decision | Pending |
| Agent SDK taskBudget + progress summaries (prior week) | Medium | Consider for Phase 5 design | Pending |
| MCP Tasks primitive (prior week) | Low | Monitor worldenergydata refactor | Pending |
| Claude Code `/voice` mode (prior week) | Low | Trial and update user_voice_prompt_tips.md | Pending |

## Top 3 Insights for PROJECT.md

1. **OrcaFlex 11.6 Python variable loads enable Phase 7 parametric sweep automation** — OrcaFlex 11.6c (Feb 2026) introduced applied loads as Python variable functions. This feature directly supports the sensitivity analysis tooling requirement in Phase 7 (solver verification gate) and the parametric design workflow in Phase 1.1 (OrcaWave automation milestone). Document Python API compatibility with Phase 7 automation framework under the Current Milestone section.

2. **Cloud-first competitor positioning (SACS Azure 10x speedup) requires GTM strategy shift** — Bentley SACS Cloud Services now delivers parallel analysis 10x faster (days → minutes) via Azure. This threatens the consultation-based pricing model for computation-heavy workflows. aceengineer differentiation must emphasize (1) standards traceability (calculation → standard reference chain), (2) domain expertise (VIV, cathodic protection, complex FFS rules), (3) parametric design insights (not raw computation). Add this positioning rationale to Key Decisions under "Consultation-based pricing."

3. **Free/low-cost calculator ecosystem (SkyCiv, TheNavalArch, CalcForge) applies margin pressure** — Emerging competitor calculators lower the barrier to entry for generic offshore calculations. aceengineer.com calculators must differentiate on specialized domains (VIV calculator unique to aceengineer, CP, spectral fatigue with DNV traceability) rather than commoditized checks (wall thickness, stability). Audit feature parity and identify gaps for differentiation roadmap.

## Cross-Domain Connections

- **OrcaFlex Python loads ↔ digitalmodel parametric sweep (Phase 7) ↔ aceengineer.com calculator differentiation** — The ability to automate parametric sweeps in OrcaFlex enables sensitivity analysis tooling (Phase 1.1 requirement). This feeds directly into aceengineer's competitive moat: clients can explore design space systematically rather than running one-off point analyses. The VIV calculator (unique to aceengineer) benefits most from this workflow.

- **SACS Cloud Services speedup ↔ aceengineer GTM positioning ↔ standards traceability value prop** — SACS's cloud parallelization commoditizes raw computation. aceengineer's value must shift to interpretation, traceability (calculation → DNV/API/ISO standard reference), and domain expertise. This reinforces the library-first digitalmodel strategy (Phase 6 decision) over SaaS/platform infrastructure investment.

- **Blue Kenue open-source mesh ↔ Phase 999.1 (ship plan CAD pipeline) ↔ Phase 999.2 (monopile/jacket foundations)** — Blue Kenue's Assimp-based mesh generation + GIS integration could reduce dependency on licensed mesh tools for both hull lofting (999.1) and hydrodynamic loading preprocessing (999.2). The open-source, cloud-friendly positioning aligns with reducing licensed software dependencies for non-solver workflows.

- **ANSYS 2026 GPU acceleration ↔ digitalmodel batch jobs ↔ licensed-win-1 infrastructure** — ANSYS's ML-based GPU resource prediction signals industry shift toward HPC. Current Phase 1 calculation modules (VIV, wall thickness, fatigue) are CPU-bound on dev-secondary. If large batch jobs become bottlenecks, GPU-aware refactoring on licensed-win-1 could enable order-of-magnitude speedups for parametric design exploration.

- **pandas 3.0 Copy-on-Write ↔ worldenergydata Parquet pipelines (Phase 2) ↔ digitalmodel calculation DataFrames** — Copy-on-Write breaking change affects both the data aggregation pipelines (worldenergydata Phase 2 completed 2026-03-26) and engineering calculation modules (digitalmodel Phase 1 completed 2026-03-25). A single compatibility audit spans both domains. String dtype changes may affect Parquet serialization logic.

- **Competitor calculator ecosystem ↔ aceengineer.com Phase 3 GTM ↔ enterprise funnel Phase 4** — SkyCiv, TheNavalArch, and CalcForge reduce demand for generic calculators. aceengineer's interactive calculators (Phase 3 shipped 2026-03-27) must drive toward consultation-qualified leads (Phase 4 enterprise funnel shipped 2026-03-28) rather than compete on free/low-cost tool access. The calculator-to-case-study CTA is the critical conversion point.

## Detailed Action Items

### Promote to PROJECT.md
- [ ] **Promote:** Add under Current Milestone (v1.1 OrcaWave Automation): "OrcaFlex 11.6c Python variable loads enable parametric sweep automation — document Python API compatibility with Phase 7 sensitivity analysis tooling"
- [ ] **Promote:** Update Key Decisions "Consultation-based pricing" entry: "Cloud-first competitor positioning (SACS Azure 10x speedup, ANSYS HPC) signals market shift. aceengineer differentiation rests on (1) standards traceability, (2) domain expertise (VIV, CP, FFS), (3) parametric design insights — not raw computation speed. Margin pressure from free/low-cost calculators (SkyCiv, TheNavalArch, CalcForge) requires specialized domain focus."
- [ ] **Promote:** Add under Engineering Domains: "Competitive landscape: SACS Cloud (Azure parallel), ANSYS 2026 GPU, SkyCiv/TheNavalArch calculators signal compute commoditization. Value anchored to standards traceability + domain expertise."

### Create GitHub Issues
- [ ] **Issue:** `digitalmodel` — Audit OrcaFlex 11.6c Python loads API for integration with Phase 7 parametric sweep framework; document compatibility
- [ ] **Issue:** `workspace-hub` — Competitive feature audit: compare aceengineer live calculators (ASME B31.4 wall thickness, DNV-RP-F109 on-bottom stability) against SkyCiv, TheNavalArch, CalcForge; identify differentiation gaps
- [ ] **Issue:** `digitalmodel` — Research ANSYS 2026 GPU acceleration for wall thickness/fatigue batch jobs; evaluate cost-benefit of GPU-aware refactor for licensed-win-1
- [ ] **Issue (carryover):** `digitalmodel` — Update spectral fatigue module to DNV-RP-C203 2024 S-N curves; benchmark 2016 vs 2024 impact
- [ ] **Issue (carryover):** `digitalmodel` — Verify ASME B31.4-2025 wall thickness clauses against current implementation
- [ ] **Issue (carryover):** `workspace-hub` — Audit tier-1 repos for pandas 3.0 compatibility (chained assignment, `.dtype == object`, string columns)
- [ ] **Issue (carryover):** `workspace-hub` — Test uv 0.11.0 TLS certificate verification on all 4 machines (especially licensed-win-1/2)
- [ ] **Issue (carryover):** `workspace-hub` — Audit all `yaml.load()` calls for `SafeLoader` usage (PyYAML security hygiene)
- [ ] **Issue (carryover):** `workspace-hub` — Audit tier-1 repos for NumPy 2.4 expired deprecations (`np.sum(generator)`, array-to-scalar)

### Add to Backlog (ROADMAP.md)
- [ ] **Backlog:** Phase 999.6 — Blue Kenue integration for hydrodynamic mesh preprocessing — evaluate for Phase 999.1 (ship plan CAD pipeline) and Phase 999.2 (monopile/jacket foundation analysis)

### Monitor Next Week
- [ ] **Monitor:** DNV 2026 hearing (closes 12 Apr 2026) for OS-C103/C105/C106 breaking changes — update YAML manifests if needed
- [ ] **Monitor:** ASME B31.4-2025 detailed clause comparison documents — specific coefficient changes not yet enumerated
- [ ] **Monitor:** GSD v1.26+ for Phase 5 nightly researcher pattern refinements
- [ ] **Monitor:** MCP Tasks primitive adoption — evaluate when first production implementations appear

### Ignore (Low Priority / Deferred)
- [ ] **Ignore:** ABS Offshore Rules website copy update (already effective 1 Jan 2026) — technical debt, no breaking impact
- [ ] **Ignore:** Claude Code `/voice` mode trial — quality-of-life improvement, not project-critical
- [ ] **Ignore:** pytest-cov/coverage.py opportunistic upgrade — no breaking changes

---

**Summary of Week's Research Impact:**

This week's findings reveal a **competitive landscape shift toward compute commoditization** (SACS Cloud 10x speedup, ANSYS GPU acceleration, free/low-cost calculators) that directly challenges aceengineer's consultation-based pricing model. The strategic response is threefold:

1. **Double down on standards traceability** — OrcaFlex 11.6 Python loads + parametric sweep automation (Phase 7) enable systematic design space exploration with full calculation→standard reference chains, which commodity calculators cannot match.

2. **Specialize in non-commoditized domains** — VIV, cathodic protection, spectral fatigue with DNV-RP-C203 2024 curves are differentiated offerings. Generic wall thickness/stability calculators face margin pressure from SkyCiv/TheNavalArch.

3. **Leverage open-source mesh/preprocessing tools** — Blue Kenue (open-source, cloud-friendly) can reduce dependency on licensed mesh software for non-solver workflows (ship plan CAD pipeline, monopile foundations), lowering operational costs while competitors invest in licensed ecosystems.

The prior week's technical debt items (pandas 3.0, uv TLS, PyYAML, DNV-RP-C203 2024, ASME B31.4-2025) remain high-priority and are carried forward as pending GitHub issues. The convergence of AI tooling maturity (GSD-2, Agent SDK, MCP Tasks) with engineering software advances (OrcaFlex Python loads, ANSYS GPU) creates an inflection point for automation-first workflows in Phase 5 (nightly research) and Phase 7 (solver verification).
