# Weekly Research Synthesis — 2026-04-17

## Action Table

| Finding | Impact | Action | Status |
|---------|--------|--------|--------|
| Agent Skills v1.0 finalized (December 2025, live across vendors) | High | Migrate `.claude/skills/` to v1.0 spec + publish to registry (immediate, not Q2) | Pending |
| Progressive disclosure 3-tier architecture production-standard | High | Implement for Phase 7 (40-60% context reduction) | Pending |
| Claude Agent Teams peer-to-peer (not hierarchical A2A) | High | Redesign Phase 7 orchestrator with shared task list pattern | Pending |
| SkillsBench +16.2pp curated skills lift (domain-critical) | High | Hand-curate Phase 5/7 skills + eval framework with 90%+ gate | Pending |
| GSD v1.34.1 gsd-researcher + gsd-debugger agents | High | Adopt for Phase 5 nightly automation + Phase 7 failure triage | Pending |
| GSD codebase intelligence (.planning/intel/ persistent store) | Medium | Import for digitalmodel/worldenergydata (Phase 7.1+ dependency tracking) | Pending |
| DNV 2026 Edition (OS-C103/105/106, NUI notation, FOWT survey) | High | Audit Phase 7 floating vessel module + incorporate NUI decision tree | Pending |
| API 579-1 Part 16 (FRP fitness assessment, expected H1/H2 2026) | Medium | When published, design RSF/PDS modules for Phase 999.2 | Monitor |
| IEC 61400-1:A1:2026 + IEC 61400-3-2:2025 + IEC TS 61400-28:2025 | Medium | Confirm alignment with DNV-ST-0126 in Phase 999.2 design inputs | Pending |
| Adaptive CP optimization (99.1% compliance, 22.5% energy savings) | High | Implement ML-based CP calculator upgrade (competitive differentiator) | Pending |
| HSC/CP material coupling (2026 standards development) | Medium | Audit wall thickness module + add interaction check to Phase 7 | Pending |
| pandas 3.0 CoW mandatory + string dtype inference | High | **BLOCKING for v1.1** — Grep chained assignment + test Parquet round-trip | Pending |
| NumPy 2.4 expired deprecations (generator, round, import reload) | High | **BLOCKING for v1.1** — Audit digitalmodel modules before Phase 7 | Pending |
| pytest-cov/coverage.py March 2026 (threshold gating standard) | Medium | Enforce 90%+ coverage gate for Phase 7 smoke tests | Pending |
| uv 0.9+ RECORD validation fix + TLS maturity | Medium | Confirm all 4 machines on post-0.9.0; test licensed-win-1 Phase 7 | Pending |
| Claude Code v2026-04 (policy enforcement, Bedrock, cost tracking) | Medium | Validate forceRemoteSettingsRefresh + benchmark cost on Phase 7 | Pending |
| MCP 2026 roadmap (transport scalability, Tasks lifecycle) | Low | Monitor for H2 2026; evaluate Phase 999.4+ multi-solver federation | Monitor |
| Sesam FOWT focus, no subsea/CP updates (H1 2026) | High | GTM positioning: specialized subsea domains (VIV, CP, fatigue) | Promote |
| SACS Cloud $13.3k/yr stable, no new modules | High | Differentiate on standards traceability + design iteration | Promote |
| OrcaFlex 11.x stable, Python API production-ready | High | Confidently target latest version for Phase 7 smoke tests | Promote |
| SkyCiv/TheNavalArch commodity calculator space fragmented | High | Avoid generic calculators; focus non-commoditized specialties | Promote |

## Top 3 Insights for PROJECT.md

### 1. **AI Infrastructure Maturity Enables Phase 7 Multi-Agent Orchestration with 40-60% Context Reduction**

Agent Skills v1.0 finalized (not Q2 draft), progressive disclosure production-standard (Layer 1/2/3 architecture), Claude Agent Teams peer-to-peer coordination (shared task lists), and GSD v1.34.1 with gsd-researcher/gsd-debugger/codebase-intelligence create a **unified harness** no vendor has shipped yet. workspace-hub can pioneer the full stack:

- **Agent Skills v1.0** — migrate `.claude/skills/` immediately (lowercase names, 1024-char descriptions, exact filename `SKILL.md`), publish 3-5 high-value skills to agentskills.io registry
- **Progressive disclosure** — restructure skills with package-level scoping (`.claude/skills/digitalmodel/`, `.claude/skills/worldenergydata/`), Layer 1 metadata (~80 tokens) loaded at session start, Layer 2 instructions (solver-specific) loaded on-demand, Layer 3 references (standards manifests) execution-only → targets 40-60% context reduction for Phase 7 dev-primary → licensed-win-1 coordination
- **Agent Teams** — **not hierarchical A2A** (prior research assumption wrong); actual implementation is peer-to-peer via shared task list → Phase 7 orchestrator assigns solver tasks to list, solver agent consumes independently, posts results → token overhead significant (~3-5M for 3-5 parallel agents) but manageable for independent L00-L06 smoke tests
- **GSD agents** — gsd-researcher (4 modes: ecosystem/feasibility/implementation/comparison) drop-in replacement for Phase 5 nightly researchers (no reimplementation); gsd-debugger (7+ investigation techniques) strengthens Phase 7 failure triage
- **SkillsBench eval framework** — curated domain-specific skills show +16.2pp average lift (+51.9pp in Healthcare domain) vs. self-generated; **hand-curation mandatory** for Phase 5/7 → implement regression evals with 90%+ gate threshold

**Recommendation:** Create 4 GitHub issues — (1) Agent Skills v1.0 compliance audit + registry publication by end April 2026, (2) progressive disclosure implementation with package scoping, (3) Phase 7 shared task list coordination schema (peer-to-peer, not hierarchy), (4) SkillsBench-style eval framework design with 10-15 canary tasks. Update PROJECT.md Workflow section to document unified harness adoption.

### 2. **Standards Currency as Competitive Moat Validated by Competitor Silence on Subsea Innovation**

Three standards updates land H1/H2 2026 (DNV 2026 Edition effective 1 July, IEC 61400-1:A1:2026, API 579-1 Part 16 expected H1/H2) while competitors show **zero subsea module innovation**:

- **Sesam** (DNV) — FOWT time-domain methods (late 2025) but zero subsea/CP/VIV/fatigue updates for 2026 H1
- **SACS** (Bentley) — Cloud parallelization stable at $13.3k/yr, no new modules announced
- **OrcaFlex** (Orcina) — 11.x series stable, Python API production-ready, no breaking changes anticipated
- **Flexcom** (Wood Group) — OpenFAST coupling for floating wind, not oil & gas subsea expansion
- **ANSYS** — GPU acceleration + Mesh Agent (AI meshing) but zero offshore/subsea-specific modules
- **SkyCiv/TheNavalArch** — commodity calculator space remains fragmented, low-cost/free tier highly competitive on generic checks (beam buckling, basic wall thickness) but **no specialized domain coverage** (VIV, CP, DNV-RP-C203 spectral fatigue)

**Market window:** aceengineer can establish specialized domain leadership before competitors react. Value anchors to:

1. **Standards traceability** — every calculation traces to current DNV/API/IEC reference with publication date + version clarity
2. **Domain expertise** — VIV calculator (unique to aceengineer), adaptive CP optimization (99.1% compliance vs. 78.3% conventional per CORROSION 2026 research), DNV-RP-C203:2024 spectral fatigue (fixes 2016 inconsistencies where lower-grade curves outperformed higher ones)
3. **Parametric design iteration** — OrcaFlex 11.6c Python variable loads enable systematic design space exploration (sensitivity analysis tooling), not one-off analyses

**Competitive positioning shift:** SACS Cloud commoditizes raw compute parallelization (days→minutes for 100+ load cases on Azure); aceengineer wins on **structured design iteration with full calculation transparency**. Generic wall thickness/stability calculators face margin compression from SkyCiv/TheNavalArch; focus on **non-commoditized specialties**.

**Recommendation:** Update PROJECT.md Key Decisions "Consultation-based pricing" entry with rationale: market consolidation (DNV/Bentley/Ramboll partnerships, 7.4% CAGR growth) + cloud-first commoditization + free/low-cost calculators apply margin pressure; value anchors to standards currency + domain expertise + parametric iteration. Create GitHub issues — (1) DNV 2026 Edition compliance audit for Phase 7 floating vessel module, (2) adaptive CP optimization implementation citing CORROSION 2026 research + Petrobras field validation, (3) HSC/CP material coupling audit for wall thickness module.

### 3. **Python Ecosystem Breaking Changes Block v1.1 Shipping Until Resolved**

Three dependency breaking changes affect completed v1.0 phases:

1. **pandas 3.0 Copy-on-Write mandatory** (released January 21, 2026) — chained assignment `df["foo"][df["bar"] > 5] = 100` no longer works; must refactor to `.loc[df["bar"] > 5, "foo"] = 100`; string dtype now infers as `str` type (was numpy object) → may affect Parquet round-trip serialization → **affects Phase 1 (digitalmodel calculations) + Phase 2 (worldenergydata Parquet pipelines)**

2. **NumPy 2.4 expired deprecations** (December 2025) — `np.sum(generator)` raises TypeError, `np.round()` always returns copy (not view), strides mutation deprecated, positional `out=` to `np.maximum`/`np.minimum` deprecated, numpy module reload in tests now fails → **affects Phase 1 (spectral fatigue, wall thickness, on-bottom stability modules)**

3. **pytest-cov + coverage.py March 2026 versions** — threshold gating (90%+) now production-standard for CI/CD; free-threading support available; AI-driven coverage gap suggestions emerging

**Blocking path:** Both Phase 1 + Phase 2 completed in v1.0 (shipped 2026-03-25/26) with ~90.5% test coverage for digitalmodel. Existing tests must pass with pandas 3.0 + NumPy 2.4 or full regression audit required before Phase 7 shipping.

**Also monitor:** uv 0.9+ RECORD validation fix (security — prevents silent file deletion on wheel uninstall), PyYAML CVE-2026-24009 SafeLoader enforcement (if Phase 1.1 integrates external client YAML, add schema validation before deserialization to prevent RCE), DNV-RP-C203:2024 S-N curves upgrade (especially C-curves for competitive differentiation), ASME B31.4-2025 low-temperature materials (enables Arctic/subsea expansion Phase 999.2).

**Recommendation:** Create 3 **BLOCKING** GitHub issues for v1.1 gate — (1) pandas 3.0 audit (grep chained assignment, test Parquet string round-trip, run v1.0 test suite on pandas 3.0), (2) NumPy 2.4 audit (refactor `np.sum(generator)`, verify test fixtures don't reload numpy, confirm copy semantics), (3) pytest-cov/coverage.py upgrade with 90%+ threshold enforcement for Phase 7. Resolve before Phase 7 planning finalized (mid-April 2026). Add to PROJECT.md Current Milestone: "Dependencies modernization (NumPy 2.4, pandas 3.0, pytest-cov March 2026) **blocking for v1.1 shipping**."

## Cross-Domain Connections

### Agent Skills Progressive Disclosure ↔ Phase 7 Multi-Agent ↔ Dependency Modernization

Progressive disclosure (Layer 1/2/3 architecture) enables dev-primary → licensed-win-1 remote execution to load solver-specific skills (OrcFxAPI integration, YAML parsing) only on licensed-win-1 while orchestrator skills remain on dev-primary (workflow routing, SSH trigger, artifact sync). Context reduction multiplies with dependency modernization: uv 0.9+ `--system-certs` + pandas 3.0 CoW + NumPy 2.4 cleanup reduce runtime edge cases. Together → 5-7 parallel subagents (Phase 7 smoke tests) without context overflow.

### OrcaFlex 11.6c Python Loads ↔ Parametric Sweeps ↔ Competitive Differentiation

OrcaFlex 11.6c's Python variable loads API (from prior research) enables automated sensitivity analysis (Phase 7 + Phase 1.1 requirement). This supports competitive positioning shift: SACS Cloud wins on raw compute parallelization (100+ load cases simultaneously on Azure), but aceengineer wins on **systematic design space exploration** with full calculation → standard traceability at each parameter point. VIV calculator (unique to aceengineer) benefits most: explore damper configurations, screening length variations, current profile assumptions parametrically. Cannot be commoditized by free calculators (SkyCiv, TheNavalArch) — requires domain expertise to define sweep grid.

### SkillsBench Regression Evals ↔ Phase 5 Nightly Researchers ↔ Phase 7 Smoke Test Reliability

Phase 5 nightly research automation (rotating domains Mon-Fri) currently lacks formal quality gates. SkillsBench-style evaluation creates feedback loop: nightly researcher failures (hallucinations, source misattribution, YAML schema violations) → extract to regression suite → prevent backsliding → improve Phase 7 solver verification reliability. Example: if nightly researcher incorrectly summarizes OrcaFlex release notes (claiming API breaking changes when none exist), that becomes canary task. When Phase 7 smoke tests rely on automated OrcFxAPI detection, regression suite protects against silent breakage.

### Market Consolidation (DNV/Bentley Partnerships) ↔ Sesam Stasis ↔ Library-First Opportunity

Sesam (DNV) announced zero new modules for 2026 H1, despite offshore software market growing 7.4% CAGR. Strategic partnerships focus on cloud infrastructure delivery, not feature innovation. This creates opportunity: aceengineer's library-first, Python-native approach (no enterprise licensing, GitHub-based collaboration, uv-managed dependencies) attracts cost-conscious engineering teams. Sesam Cloud Compute (via Veracity) requires enterprise negotiation; aceengineer consultation pricing ($500-2000) is 10x lower entry cost. Phase 999.2 (Wind/Turbine FFS) targets Sesam-adjacent domains with differentiated open-standards tooling.

### pandas 3.0 CoW ↔ Parquet Pipelines ↔ Calculation DataFrames ↔ Phase 2 Validation

Copy-on-Write breaking change affects both completed phases: Phase 2 (worldenergydata Parquet pipelines shipped 2026-03-26) and Phase 1 (digitalmodel modules shipped 2026-03-25). Chained assignment pattern silently fails with CoW semantics. String dtype changes may affect Parquet serialization. Single compatibility audit spans both domains: grep `df[...][...] = ` across tier-1 repos, test Parquet write → read with string columns, verify calculation module test coverage catches CoW edge cases.

### PyYAML CVE-2026-24009 ↔ Phase 5 YAML Manifests ↔ Phase 7 Job Configs ↔ External Client Data Risk

RCE vulnerability occurs when downstream libraries internally use `yaml.load()` without `SafeLoader`. Workspace-hub's `.planning/research/` YAML manifests (Phase 5) and Phase 7 solver job configs are currently trusted inputs, but **if Phase 1.1 integrates client-supplied OrcaFlex job files in YAML format** (e.g., vessel specification YAML from external design teams), untrusted YAML deserialization becomes RCE vector. Security audit: grep all repos for `yaml.load()`, enforce `SafeLoader`, and if external YAML integration planned, add schema validation layer (Pydantic model validation) **before** YAML deserialization.

### DNV-RP-C203:2024 S-N Curves ↔ Spectral Fatigue ↔ Competitive Differentiation

2024 revision (October 2024) fixes inconsistencies where lower-grade curves outperformed higher ones (B1 nearly identical to 2016, C-curves show significant improvement). digitalmodel's spectral fatigue module (Phase 1 completed 2026-03-25) uses 2016 curves. Upgrading to 2024 affects all calculations and benchmarks (L00-L06 examples). This is both **technical debt** (standards currency) and **competitive differentiation** (SkyCiv, TheNavalArch unlikely to track DNV 2024 updates rapidly). aceengineer can position as "standards-current by default" — Phase 1.1 calculation reports cite DNV-RP-C203:2024, not 2016. Benchmark delta measurement (especially C-curves) quantifies accuracy improvement for client-facing value prop.

### ASME B31.4-2025 Equation Unification ↔ Wall Thickness ↔ Low-Temperature Materials ↔ Phase 999.2 Arctic Expansion

2025 edition eliminated separate US/SI equation sets (simplifies code, requires unit-aware verification) and added low-temperature material requirements. digitalmodel's wall thickness module (Phase 1) must audit equation equivalence. Low-temperature materials enable **new calculation domain**: Arctic offshore, subsea cold-water pipelines, cryogenic LNG. Aligns with Phase 999.2 backlog (Wind Energy, Turbines & Fitness-for-Service) — marine structure FFS in Arctic/cold regions is natural extension. Document as future capability in aceengineer GTM positioning.

## Detailed Action Items

### Promote to PROJECT.md

- [ ] **Add to Workflow section:** "Agent Skills v1.0 (finalized December 2025, live across Claude Code, Codex, Google ADK, VS Code, Cursor) standardizes SKILL.md format. All workspace-hub skills in `.claude/skills/` target v1.0 spec (lowercase name max 64 chars hyphens only, description max 1024 chars, exact filename `SKILL.md`). Migration removes registry publication risk; publish high-value skills to agentskills.io (gsd-researcher, Phase 5 nightly automation, Phase 7 solver orchestrator). Progressive disclosure (3-tier: L1 metadata ~80 tokens, L2 instructions on-demand, L3 references execution-only) targets 40-60% context reduction for Phase 7 multi-agent orchestration."

- [ ] **Add to Current Milestone (v1.1 OrcaWave Automation):** "Dependencies modernization (NumPy 2.4, pandas 3.0, pytest-cov/coverage.py March 2026 versions) **blocking for v1.1 shipping**. Audit complete by Phase 7 gate. Agent Skills v1.0 adopted for cross-vendor interoperability (Codex, Gemini CLI). uv post-0.9.0 standard across 4 machines (RECORD validation + TLS stability). Phase 7 solver verification implements Agent Teams peer-to-peer coordination via shared task list (not orchestrator-subordinate hierarchy). Token overhead significant (~3-5M for 3-5 parallel agents); evaluate on 1-2 smoke tests before full L00-L06 batch."

- [ ] **Update Key Decisions "Consultation-based pricing" entry:** "Market consolidation (DNV/Bentley/Ramboll partnerships, 7.4% CAGR growth $750M→$818M 2025→2026) + cloud-first commoditization (SACS Azure 10x speedup $13.3k/yr, ANSYS GPU) + free/low-cost calculators (SkyCiv, TheNavalArch) apply margin pressure. aceengineer value anchors to: (1) standards traceability (calculation → DNV/API/ISO reference chain), (2) domain expertise (VIV, adaptive cathodic protection, DNV-RP-C203:2024 spectral fatigue), (3) parametric design iteration (systematic design space exploration). Generic wall thickness/stability calculators unsustainable at consultation pricing. Focus on specialized domains validated by competitor silence on subsea innovation (Sesam FOWT-focused, SACS Cloud parallelization only, no new VIV/CP/fatigue modules 2026 H1)."

- [ ] **Add to Engineering Domains:** "Competitive landscape 2026 H1: Sesam FOWT-focused (zero subsea/CP updates), SACS Cloud stable ($13.3k/yr, no new modules), OrcaFlex 11.x Python API production-ready, OpenFAST marine preprocessing (not riser dynamics), SkyCiv/TheNavalArch free calculators (generic checks only). Standards currency as moat: DNV 2026 Edition (effective 1 July, OS-C103/105/106 restructure, NUI notation, FOWF survey overhaul), IEC 61400-1:A1:2026 + IEC 61400-3-2:2025 + IEC TS 61400-28:2025 (complete wind turbine ecosystem), API 579-1 Part 16 (FRP fitness assessment expected H1/H2 2026). ASME B31.4-2025 low-temperature materials enable Arctic/subsea expansion (Phase 999.2)."

### Create GitHub Issues (Blocking for v1.1)

- [ ] **`digitalmodel` + `worldenergydata` — BLOCKING:** Complete pandas 3.0 Copy-on-Write audit; grep for chained assignment `df[...][...] = ` → refactor all to `.loc[..., ...] = `; test Parquet write → read round-trip with string columns on pandas 3.0; run full v1.0 test suite (Phase 1-6 regression). Document CoW semantics in calculation DataFrame documentation. **Timeline:** finish before Phase 7 planning finalized.

- [ ] **`digitalmodel` — BLOCKING:** Complete NumPy 2.4 deprecation audit; identify and refactor all `np.sum(generator)` → `np.sum(np.fromiter())` or builtin `sum()`; verify test fixtures don't reload numpy module; confirm all `np.round()` calls assume copy semantics (not view); remove positional `out=` from `np.maximum`/`np.minimum`; update type-checker configuration for `np.arange(start=...)` → positional form. **Priority:** block Phase 7 gate until resolved.

- [ ] **`workspace-hub` CI/CD — BLOCKING:** Upgrade CI/CD gate scripts to require pytest-cov + coverage.py >= 7.13.5 (March 2026); set threshold enforcement to 90%+ for Phase 7 smoke tests + all tier-1 repos. Document free-threading implications if Phase 7 uses multi-threaded agents.

### Create GitHub Issues (High Priority)

- [ ] **`workspace-hub`:** Migrate `.claude/skills/` to Agent Skills v1.0 spec; audit ~900 lines for YAML compliance (name format lowercase max 64 chars + hyphens only, description max 1024 chars, filename exactly `SKILL.md`); measure compliance percentage; fix violations atomically; publish 3-5 high-value skills to agentskills.io registry by end April 2026 (gsd-researcher, Phase 5 nightly automation, Phase 7 solver orchestrator).

- [ ] **`workspace-hub`:** Implement progressive disclosure for multi-repo context; restructure `.claude/skills/` with package-level scoping (`.claude/skills/digitalmodel/`, `.claude/skills/worldenergydata/`); Layer 1 metadata ~80 tokens (session start), Layer 2 instructions (solver-specific, on-demand), Layer 3 references (standards manifests, execution-only); target 40-60% context reduction for Phase 7 dev-primary → licensed-win-1 coordination.

- [ ] **`workspace-hub`:** Design Phase 7 shared task list coordination schema for Agent Teams peer-to-peer execution: task ID (globally unique per phase), solver job spec (YAML with example L00-L06 ID + OrcFxAPI parameters), result artifact path (S3/local store), completion status (pending/executing/success/failed/expired). Implement coordinator that assigns tasks, monitors completion, retries failures (max 2), expires results after 24h. Budget token overhead: 3M for 3 agents, 5M for 5 agents; test on 2-3 smoke tests before full L00-L06 batch. Document in Phase 7 PLAN.md with sequence diagram.

- [ ] **`workspace-hub`:** Design skill evaluation framework for Phase 5 + Phase 7 using SkillsBench model: (1) define 10-15 canary tasks (OrcFxAPI smoke test, YAML manifest validation, calculation accuracy benchmarks), (2) measure pass rate lift from curated Phase 5 nightly researcher skills vs. baseline, (3) implement Braintrust-style regression gates (GitHub Action on PR, 90%+ gate threshold), (4) extract Phase 5 production failures to regression test cases weekly.

- [ ] **`workspace-hub`:** Adopt GSD v1.34.1 gsd-researcher agent for Phase 5 nightly automation; measure output quality (source accuracy, hallucination rate) vs. current hand-crafted researchers; migrate Phase 5 to gsd-researcher for 4 research modes (ecosystem/feasibility/implementation/comparison) by mid-May 2026.

- [ ] **`workspace-hub`:** Benchmark Phase 5 nightly researchers on Gemini CLI (dev-secondary) vs. current Claude Code; measure token efficiency, cost (free tier 1k req/day), output quality (hallucination rate, source attribution); if 20%+ improvement on cost/token, migrate Phase 5 to Gemini CLI (dev-secondary) to free Claude Code budget for Phase 7.

- [ ] **`digitalmodel`:** Audit floating vessel module compatibility with DNV 2026 Edition (OS-C103/105/106 restructure, effective 1 July 2026); verify TLP/CS-A/B/C analysis logic; incorporate NUI notation (personnel-free design) as optional analysis scenario; document DNV 2026 applicability in Phase 7 calculation reports.

- [ ] **`digitalmodel`:** Implement adaptive CP optimization model for anodic current distribution (ML-based or constraint-based); benchmark against DNV-RP-B401 conventional design; cite CORROSION 2026 research (99.1% potential compliance, 22.5% energy savings) + Petrobras field validation; position as **competitive differentiator** vs. SkyCiv/TheNavalArch commodity CP tools.

- [ ] **`digitalmodel`:** Audit wall thickness module + Phase 7 smoke tests for HSC/CP material selection interaction check; verify material-CP potential coupling logic against emerging 2026 standards guidance; document material HSC risk in Phase 1.1 calculation reports; gate Phase 7 with material-potential validation checks.

- [ ] **`workspace-hub` + tier-1 repos:** Verify all 4 machines running uv post-0.9.0 stable (RECORD validation + TLS maturity); run Phase 7 smoke test on licensed-win-1 with current uv binary; confirm `uv pip install` with certificate chain validation; document uv version pinning in CI/CD gate scripts.

- [ ] **`workspace-hub`:** Validate Claude Code v2026-04 policy enforcement (forceRemoteSettingsRefresh) with licensed-win-1 setup; document credential validation chain for remote orchestration; benchmark cost tracking feature on Phase 7 smoke test execution; establish token budget guardrails (dev-primary orchestrator: 100k tokens/cycle, licensed-win-1 solver: 500k max).

### Create GitHub Issues (Medium Priority)

- [ ] **`digitalmodel` + `worldenergydata`:** Implement GSD codebase intelligence import using gsd-intel-updater; persist `.planning/intel/` JSON files (files, exports, symbols, patterns, dependencies); enable Phase 7.1+ intelligent solver state inspection queries; document intelligence query API.

- [ ] **`digitalmodel`:** When API 579-1 Part 16 publishes (expected H1/H2 2026), audit technical requirements for FRP composite fitness assessment; design RSF/PDS calculation modules; add Level 1/2/3 assessment framework to Phase 999.2 roadmap (FRP riser, umbilical, hybrid CRA-composite).

- [ ] **`digitalmodel`:** Confirm IEC 61400-1:2019/A1:2026, IEC 61400-3-2:2025, IEC TS 61400-28:2025 alignment with DNV-ST-0126 in monopile/jacket design input specifications; document harmonized DEL/NTM90/EWM load methodology; flag IEC TS 61400-28:2025 as prerequisite for Phase 999.7+ (structural integrity management automation).

- [ ] **`digitalmodel`:** Upgrade spectral fatigue module to DNV-RP-C203:2024 S-N curves; benchmark L00-L06 examples against 2016 baseline; update standards traceability manifests; measure fatigue strength delta (especially C-curves for competitive differentiation).

- [ ] **`digitalmodel`:** Audit ASME B31.4-2025 vs. 2016/2020 wall thickness equations; verify unit unification doesn't change calculation logic; document low-temperature material requirements for Phase 999.2 Arctic/subsea expansion.

- [ ] **`workspace-hub`:** Security audit: grep all code for `yaml.load()` without `SafeLoader`; if Phase 5/7 accept external YAML (client OrcaFlex job files), add schema validation layer (Pydantic models) before deserialization to prevent CVE-2026-24009 RCE.

### Monitor Next Week

- [ ] **Agent Skills v1.0 → v1.1 transition** (expected Q3 2026) — track [agentskills/agentskills](https://github.com/agentskills/agentskills) and [anthropics/skills](https://github.com/anthropics/skills) for breaking changes.

- [ ] **GSD framework v1.35** (expected Q2 2026) — signal for codebase intelligence hardening (Phase 999.4 prerequisite) or multi-runtime support expansion.

- [ ] **Agent Teams graduation from experimental → public beta** (expected Q2 2026 if usage stabilizes) — design Phase 7 task list coordination as production feature.

- [ ] **MCP transport scalability RFC or pre-spec** (expected H2 2026) — evaluate for Phase 999.4+ multi-solver federation architecture.

- [ ] **API 579-1 Part 16 publication** — when released, implement FRP fitness assessment modules for Phase 999.2.

- [ ] **Sesam 2026 H2 announcements** — check DNV conferences (Offshore Technology Conference April 2026, DNV Seminars June 2026) for technology roadmap; if major updates, reassess competitive positioning.

- [ ] **Claude Code minor updates** (May 2026) — watch for policy controls maturity, cost tracking UX improvements, configuration drift issues on licensed machines.

### Ignore (Low Priority)

- [ ] AGENTS.md format standardization — Agent Skills uses SKILL.md; current `.claude/agents/*.md` files remain valid during migration window.

- [ ] Flexcom 2026 updates — specialized niche, no client demand signal yet.

- [ ] Sesam pricing — enterprise negotiated licensing, competitively irrelevant at consultation pricing tier.

- [ ] Bedrock GPU support — not relevant for Phase 7 orchestration; re-evaluate only if Phase 1.1 adopts cloud parallelization.

- [ ] LangGraph 2026 updates — GSD + Agent Teams are workspace-hub's primary coordination patterns; no migration value.

---

## Summary

This week's research reveals **three strategic inflection points** converging at Phase 7 v1.1 gate:

### 1. AI Infrastructure Maturity Creates Unified Orchestration Harness

Agent Skills v1.0 finalized (immediate registry publication), progressive disclosure production-standard (40-60% context reduction), Claude Agent Teams peer-to-peer (shared task lists, not hierarchical), GSD v1.34.1 agents (gsd-researcher/gsd-debugger/codebase-intelligence), and SkillsBench regression evals (+16.2pp average, +51.9pp in specialized domains) create **compounding improvement cycle** no vendor has shipped yet. workspace-hub can pioneer full stack integration.

### 2. Standards Currency as Competitive Moat Validated by Competitor Inaction

DNV 2026 Edition (1 July effective), IEC 61400-1:A1:2026, API 579-1 Part 16 (H1/H2 2026) land while competitors announce **zero subsea innovation** (Sesam FOWT-focused, SACS Cloud parallelization only, OrcaFlex stable, no new VIV/CP/fatigue modules). Market window for specialized domain leadership: adaptive CP optimization (99.1% compliance vs. 78.3% conventional), DNV-RP-C203:2024 spectral fatigue (fixes 2016 inconsistencies), parametric design iteration (vs. cloud parallelization opacity). Commodity calculators (SkyCiv/TheNavalArch) remain low-cost/free but lack specialized coverage.

### 3. Python Ecosystem Breaking Changes Block Shipping Until Resolved

pandas 3.0 CoW mandatory (chained assignment pattern broken), NumPy 2.4 expired deprecations (generator summation, round semantics, import reload), pytest-cov March 2026 threshold gating — all affect completed v1.0 phases. **BLOCKING for v1.1:** Must audit + refactor before Phase 7 gate. Timeline: mid-April 2026 resolution before Phase 7 planning finalized.

**Net assessment:** Phase 7 positioned for execution success. Agent Skills + progressive disclosure + peer coordination + GSD agents + regression evals provide foundation; standards currency + competitor silence create market window; dependency modernization is blocking gate. Resolve pandas/NumPy audits immediately, migrate skills to v1.0 spec by end April, implement progressive disclosure + shared task list coordination, adopt gsd-researcher for Phase 5, design SkillsBench eval framework with 90%+ gate.
