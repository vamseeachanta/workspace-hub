# Weekly Research Synthesis — 2026-04-10

## Action Table

| Finding | Impact | Action | Status |
|---------|--------|--------|--------|
| Agent Skills open standard (v1.0 Q2 2026) | High | Migrate `.claude/skills/` to SKILL.md spec by Q2 + publish to registry | Pending |
| Progressive disclosure 3-tier architecture | High | Refactor skills for 40-60% context reduction (Phase 7 multi-agent) | Pending |
| SkillsBench + Braintrust regression evals | High | Design eval framework for Phase 5/7 with 90%+ gate | Pending |
| Hierarchical A2A delegation protocol | High | Map Phase 7 orchestrator/solver skill boundaries | Pending |
| OrcaFlex 11.6c Python variable loads | High | Document API compatibility for Phase 7 parametric sweeps | Pending |
| SACS Cloud 10x speedup ($13.3k/yr) | High | GTM positioning shift: traceability > raw compute | Pending |
| Market consolidation (7.4% CAGR, partnerships) | High | Differentiate on VIV/CP/fatigue, not generic calculators | Pending |
| uv 0.11.0 TLS `--system-certs` (prior week) | High | 4-machine compatibility test + Phase 7 remote execution | Pending |
| pandas 3.0 Copy-on-Write (prior week) | High | Audit `.loc` refactor across tier-1 repos | Pending |
| DNV-RP-C203 2024 S-N curves (prior week) | High | Spectral fatigue module upgrade + benchmark | Pending |
| ASME B31.4-2025 equation unification (prior week) | High | Wall thickness module equivalence audit | Pending |
| PyYAML CVE-2026-24009 SafeLoader (prior week) | High | Security audit all `yaml.load()` calls | Pending |
| NumPy 2.4 generator deprecations (prior week) | Medium | Refactor `np.sum(generator)` → `np.fromiter()` | Pending |
| Production failures → eval suite feedback loop | Medium | Extract Phase 5 failures to regression tests | Pending |
| Sesam unchanged 2026, no new modules | Medium | Monitor DNV conferences for roadmap signals | Pending |
| OpenFAST v5.0 marine extensions | Medium | Evaluate for Phase 999.2 integration if roadmap shifts | Pending |
| Blue Kenue open-source mesh | Low | Phase 999.1 mesh dependency reduction | Pending |

## Top 3 Insights for PROJECT.md

1. **Agent Skills open standard + progressive disclosure unlock cross-vendor skill interoperability and 40-60% context reduction** — The agentskills.io v0.9 spec (v1.0 Q2 2026) standardizes SKILL.md format across Claude Code, Cursor, Gemini CLI, and Codex CLI. This enables workspace-hub's 900+ lines of GSD skills to be published to a universal registry and used by other teams. Combining this with progressive disclosure (3-tier metadata → instructions → resources architecture) could reduce Phase 7 multi-agent orchestration context load by 40-60%. This is critical infrastructure for the solver verification gate, where 3+ subagents coordinate across dev-primary → licensed-win-1 remote execution. **Recommendation:** Migrate `.claude/skills/` to SKILL.md spec by end Q2 2026, implement progressive disclosure with package-level scoping (`.claude/skills/digitalmodel/`, `.claude/skills/worldenergydata/`), and publish high-value skills (gsd-researcher, Phase 5 nightly automation) to agentskills.io registry.

2. **Market consolidation toward cloud-first delivery + strategic partnerships forces aceengineer GTM pivot: standards traceability > raw compute speed** — This week's competitive intelligence confirms the strategic shift documented in prior research: SACS Cloud (Bentley Azure parallel, 10x speedup, $13.3k/yr), offshore software market growing 7.4% CAGR ($750M→$818M 2025→2026), and DNV/Bentley/Ramboll/John Wood strategic partnerships consolidating the ecosystem. Cloud parallelization commoditizes raw computation (days→minutes for 100+ load cases). aceengineer's consultation-based pricing ($500-2000/engagement) is sustainable **only** if value anchors to: (1) **standards traceability** (calculation → DNV/API/ISO reference chain that commodity calculators lack), (2) **domain expertise** (VIV, cathodic protection, spectral fatigue with DNV-RP-C203 2024 curves), and (3) **parametric design iteration** (systematic design space exploration, not one-off analyses). Generic wall thickness/stability calculators face margin compression from free/low-cost competitors (SkyCiv, TheNavalArch, CalcForge). **Recommendation:** Update PROJECT.md Key Decisions section to document this positioning rationale; audit aceengineer.com live calculators for differentiation gaps; emphasize specialized domains in Phase 3 GTM copy.

3. **SkillsBench + Braintrust regression evals + production failures → eval suite feedback loop establishes path to self-improving skill quality** — Industry-standard agent skill evaluation pattern: (1) define canary tasks with deterministic checks + rubric grading, (2) extract production failures and add to regression suite (preventing backsliding), (3) gate releases with 90%+ pass rate, (4) track score delta over time. This directly applies to workspace-hub Phase 5 (nightly research automation) and Phase 7 (solver verification smoke tests). Current failure modes (research hallucinations, YAML manifest validation errors, OrcFxAPI connection issues) can be systematized into eval cases. Combined with Agent Skills open standard, this creates a compounding improvement loop: each production failure strengthens eval suite → regression detection improves → skill quality increases → fewer production failures. **Recommendation:** Design Phase 5/7 evaluation framework with 10-15 canary tasks, capture nightly researcher failures as regression tests, implement Braintrust-style scoring (prompt → trace → checks → score), and gate Phase 7 releases with 90%+ pass threshold.

## Cross-Domain Connections

- **Agent Skills progressive disclosure ↔ Phase 7 multi-agent orchestration ↔ uv/pandas/NumPy dependency modernization** — The 3-tier metadata architecture (Layer 1: name + one-liner ~80 tokens, Layer 2: full instructions, Layer 3: references/) enables Phase 7's dev-primary → licensed-win-1 remote execution pattern to load only solver-specific skills on licensed-win-1 (OrcFxAPI integration, YAML parsing) while orchestrator skills remain on dev-primary (workflow routing, SSH trigger, artifact sync). This context reduction is multiplicative with dependency modernization: uv 0.11.0 `--system-certs` + pandas 3.0 CoW + NumPy 2.4 cleanup reduce runtime edge cases, progressive disclosure reduces agent context load. Together, these changes enable 5-7 parallel subagents (Phase 7 smoke tests) without context overflow.

- **OrcaFlex 11.6c Python variable loads ↔ parametric sweep automation ↔ aceengineer differentiation on design iteration** — OrcaFlex 11.6c's Python variable loads API enables automated sensitivity analysis (Phase 7 target + Phase 1.1 requirement). This directly supports the competitive positioning shift: SACS Cloud wins on raw compute parallelization (100+ load cases simultaneously on Azure), but aceengineer wins on **systematic design space exploration** with full calculation → standard traceability at each parameter point. The VIV calculator (unique to aceengineer) benefits most: clients can explore damper configurations, screening length variations, and current profile assumptions parametrically rather than running one-off analyses. This workflow cannot be commoditized by free calculators (SkyCiv, TheNavalArch) because it requires domain expertise to define the parameter sweep grid.

- **SkillsBench regression evals ↔ Phase 5 nightly researchers ↔ Phase 7 smoke test reliability** — Phase 5 nightly research automation (rotating domains Mon-Fri, outputs to `.planning/research/`) currently lacks formal quality gates. Implementing SkillsBench-style evaluation creates a feedback loop: nightly researcher failures (hallucinations, source misattribution, YAML schema violations) → extract to regression suite → prevent backsliding → improve Phase 7 solver verification reliability. For example: if a nightly researcher incorrectly summarizes OrcaFlex release notes (claiming API breaking changes when none exist), that failure becomes a canary task ("summarize OrcaFlex 11.6c changes without hallucination"). When Phase 7 smoke tests rely on automated OrcFxAPI detection, the regression suite protects against silent breakage.

- **Market consolidation (DNV/Bentley/Ramboll partnerships) ↔ Sesam stasis (no 2026 modules) ↔ aceengineer library-first opportunity** — Sesam (DNV) announced zero new modules for 2026 H1, despite offshore software market growing 7.4% CAGR. Strategic partnerships focus on cloud infrastructure delivery, not feature innovation. This creates market opportunity: aceengineer's library-first, Python-native approach (no enterprise licensing, GitHub-based collaboration, uv-managed dependencies) attracts cost-conscious engineering teams. Sesam Cloud Compute (via Veracity) requires enterprise negotiation; aceengineer consultation pricing ($500-2000) is 10x lower entry cost. Phase 999.2 (wind/turbine FFS) targets Sesam-adjacent domains with differentiated open-standards tooling.

- **pandas 3.0 Copy-on-Write ↔ worldenergydata Parquet pipelines ↔ digitalmodel calculation DataFrames ↔ Phase 2 completion validation** — Copy-on-Write breaking change affects both completed phases: Phase 2 (worldenergydata Parquet pipelines shipped 2026-03-26) and Phase 1 (digitalmodel modules shipped 2026-03-25). Chained assignment pattern `df["foo"][df["bar"] > 5] = 100` silently fails with CoW semantics → must refactor to `.loc[df["bar"] > 5, "foo"] = 100`. String dtype changes may affect Parquet round-trip serialization. A single compatibility audit spans both domains. Grep for `df[...][...] = ` across tier-1 repos, test Parquet write → read with string columns, verify calculation module test coverage catches CoW edge cases.

- **PyYAML CVE-2026-24009 shadow vulnerability ↔ Phase 5 YAML manifests ↔ Phase 7 job configs ↔ external client data integration risk** — The RCE vulnerability occurs when downstream libraries (Docling, others) internally use `yaml.load()` without `SafeLoader`. Workspace-hub's `.planning/research/` YAML manifests (Phase 5 nightly researchers) and Phase 7 solver job configs are currently trusted inputs, but **if Phase 1.1 integrates client-supplied OrcaFlex job files in YAML format** (e.g., vessel specification YAML from external design teams), untrusted YAML deserialization becomes an RCE vector. Security audit: grep all repos for `yaml.load()`, enforce `SafeLoader`, and if external YAML integration is planned, add schema validation layer (e.g., Pydantic model validation) **before** YAML deserialization.

- **DNV-RP-C203 2024 S-N curves ↔ spectral fatigue module ↔ aceengineer competitive differentiation ↔ Phase 1 validation** — The 2024 revision (October 2024) fixes inconsistencies where lower-grade curves outperformed higher ones (B1 nearly identical to 2016, C-curves show significant improvement). digitalmodel's spectral fatigue module (Phase 1 completed 2026-03-25) uses 2016 curves. Upgrading to 2024 curves affects all existing calculations and benchmarks (L00–L06 examples). This is both **technical debt** (standards currency) and **competitive differentiation** (SkyCiv, TheNavalArch, CalcForge unlikely to track DNV 2024 updates as rapidly). aceengineer can position as "standards-current by default" — Phase 1.1 calculation reports cite DNV-RP-C203:2024, not 2016. Benchmark delta measurement (especially C-curves) quantifies the accuracy improvement for client-facing value prop.

- **ASME B31.4-2025 equation unification ↔ wall thickness module ↔ low-temperature materials ↔ Phase 999.2 Arctic/subsea expansion** — The 2025 edition eliminated separate US/SI equation sets (simplifies code, requires unit-aware verification) and added low-temperature material requirements. digitalmodel's wall thickness module (Phase 1) must audit equation equivalence: current implementation vs. 2025 revision longitudinal stress (SL) calculations now match B31.3 methodology. The low-temperature material requirements enable **new calculation domain**: Arctic offshore, subsea cold-water pipelines, cryogenic LNG systems. This aligns with Phase 999.2 backlog (Wind Energy, Turbines & Fitness-for-Service) — marine structure FFS in Arctic/cold regions is natural extension. Document as future capability in aceengineer GTM positioning.

## Detailed Action Items

### Promote to PROJECT.md

- [ ] **Promote:** Add under Workflow section: "Agent Skills open standard (agentskills.io v0.9, v1.0 Q2 2026) unifies SKILL.md format across Claude Code, Cursor, Gemini CLI, Codex CLI. All workspace-hub skills in `.claude/skills/` target v0.9 spec by Q2 2026 end for cross-vendor interoperability + registry publication."

- [ ] **Promote:** Update Key Decisions "Consultation-based pricing" entry: "Market consolidation (DNV/Bentley/Ramboll partnerships, 7.4% CAGR growth) + cloud-first commoditization (SACS Azure 10x speedup $13.3k/yr, ANSYS GPU) + free/low-cost calculators (SkyCiv, TheNavalArch, CalcForge) apply margin pressure. aceengineer value anchors to: (1) standards traceability (calculation → DNV/API/ISO reference chain), (2) domain expertise (VIV, cathodic protection, DNV-RP-C203 2024 spectral fatigue), (3) parametric design iteration (systematic design space exploration). Generic wall thickness/stability calculators unsustainable at consultation pricing. Focus on specialized domains."

- [ ] **Promote:** Add under Current Milestone (v1.1 OrcaWave Automation): "OrcaFlex 11.6c Python variable loads enable parametric sweep automation (Phase 7 sensitivity analysis tooling + Phase 1.1 design exploration). Progressive disclosure (3-tier skill architecture) targets 40-60% context reduction for multi-agent orchestration (dev-primary → licensed-win-1 remote execution). SkillsBench-style eval framework gates Phase 7 smoke tests with 90%+ reliability threshold."

- [ ] **Promote:** Add under Engineering Domains: "Competitive landscape 2026: SACS Cloud (Azure parallel), ANSYS GPU, Sesam stasis (zero new modules), SkyCiv/TheNavalArch free calculators signal compute commoditization. Value anchored to standards currency (DNV-RP-C203 2024, ASME B31.4-2025) + domain expertise. ASME B31.4-2025 low-temperature materials enable Arctic/subsea expansion (Phase 999.2)."

### Create GitHub Issues

- [ ] **Issue:** `workspace-hub` — Migrate `.claude/skills/` to Agent Skills v0.9 spec (SKILL.md format, YAML metadata); target Q2 2026 completion; publish high-value skills (gsd-researcher, Phase 5 nightly automation) to agentskills.io registry

- [ ] **Issue:** `workspace-hub` — Implement progressive disclosure for multi-repo context: audit `.claude/skills/` for 3-tier architecture (L1 metadata ~80 tokens, L2 instructions, L3 references/); move domain-specific content to package-level scoping (`.claude/skills/digitalmodel/`, `.claude/skills/worldenergydata/`); target 40-60% context reduction for Phase 7 multi-agent orchestration

- [ ] **Issue:** `workspace-hub` — Design skill evaluation framework for Phase 5 + Phase 7: (1) define 10-15 canary tasks (OrcFxAPI smoke test, YAML manifest validation, calculation accuracy benchmarks), (2) extract nightly researcher failures as regression tests, (3) implement Braintrust-style eval (prompt → trace → checks → score), (4) gate Phase 7 releases with 90%+ pass rate

- [ ] **Issue:** `workspace-hub` — Map Phase 7 multi-agent skill delegation boundaries: (1) orchestrator skills (dev-primary): workflow routing, remote SSH trigger, artifact sync, (2) solver skills (licensed-win-1): OrcFxAPI integration, YAML parsing, result extraction, (3) shared skills (both): YAML validation, standards traceability checks; formalize via A2A protocol documentation in Phase 7 PLAN.md

- [ ] **Issue:** `digitalmodel` — Document OrcaFlex 11.6c Python variable loads API compatibility for Phase 7 parametric sweep framework + Phase 1.1 sensitivity analysis tooling; verify API stability for automated design space exploration

- [ ] **Issue:** `workspace-hub` — Competitive feature audit: compare aceengineer live calculators (ASME B31.4 wall thickness, DNV-RP-F109 on-bottom stability, VIV) against SkyCiv, TheNavalArch, CalcForge; identify differentiation gaps; document specialized domains for GTM positioning

- [ ] **Issue (carryover):** `workspace-hub` — Audit tier-1 repos for uv 0.11.0 TLS compatibility; test `uv pip install` with `--system-certs` on all 4 machines (especially licensed-win-1/2); document certificate chain requirements for Phase 7 remote execution

- [ ] **Issue (carryover):** `digitalmodel` + `worldenergydata` — Audit pandas 3.0 Copy-on-Write compatibility; grep all repos for chained assignment `df[...][...] = ` → refactor to `.loc[..., ...] = `; benchmark Parquet string dtype round-trip serialization

- [ ] **Issue (carryover):** `digitalmodel` — Upgrade spectral fatigue module to DNV-RP-C203 2024 S-N curves; benchmark L00–L06 examples against 2016 baseline; update standards traceability manifests; measure fatigue strength delta (especially C-curves for competitive differentiation)

- [ ] **Issue (carryover):** `digitalmodel` — Audit ASME B31.4-2025 vs. 2016/2020 wall thickness equations; verify unit unification doesn't change calculation logic; document low-temperature material requirements for Phase 999.2 Arctic/subsea expansion

- [ ] **Issue (carryover):** `workspace-hub` — Security audit: grep all code for `yaml.load()` without `SafeLoader`; if Phase 5/7 accept external YAML (client OrcaFlex job files), add schema validation layer (Pydantic models) before deserialization to prevent CVE-2026-24009 RCE

- [ ] **Issue (carryover):** `digitalmodel` — Refactor NumPy 2.4 deprecations: replace `np.sum(generator)` → `np.sum(np.fromiter())` or builtin `sum()`; verify all array rounding logic assumes copy semantics (not view) per `np.round()` behavior change

### Add to Backlog (ROADMAP.md)

- [ ] **Backlog:** Phase 999.6 — Agent skill autoresearch generalization: extend skill-autoresearch-nightly.sh loop to iterate on agent definitions (`.claude/agents/`), research templates (`.claude/get-shit-done/templates/`), and workflow configs; abstract runner to accept target type + eval function; track results per-target-type with same safety model (branch isolation, human review)

- [ ] **Backlog:** Phase 999.7 — High-iteration autoresearch with compounding improvements: increase from single-pass to 5-12 iterations/target/night (~180s/iteration budget); sequential accept/reject within target (accepted changes carry forward); budget guard + diminishing returns detection (stop after 3 no-improvement iterations); track cost-per-improvement to optimize iteration count

### Monitor Next Week

- [ ] **Monitor:** Agent Skills spec v1.0 release (Q2 2026 deadline) — when published, audit workspace-hub SKILL.md compliance and publish to agentskills.io registry

- [ ] **Monitor:** Sesam 2026 H2 announcements — check DNV conferences (Offshore Technology Conference April 2026, DNV Seminars June 2026) for technology roadmap signals; if major updates (AI-driven design optimization, cloud parity with SACS), reassess competitive positioning

- [ ] **Monitor:** OpenFAST monopile/jacket subsea foundation modules — current v5.0 focuses marine energy; if NREL adds fixed-bottom jacket analysis (oil & gas-relevant), evaluate for Phase 999.2 integration

- [ ] **Monitor:** SACS Cloud Azure parallel architecture for large batch jobs — if Phase 1.1 OrcaWave sensitivity analysis requires 100+ load cases, research SACS Cloud cost model vs. licensed-win-1 GPU acceleration; current planning assumes single-node execution

### Ignore (Low Priority / Deferred)

- [ ] **Ignore:** AGENTS.md format standardization — Agent Skills spec uses SKILL.md as canonical; current `.claude/agents/*.md` files remain valid during migration window; update naming when convenient, no breaking change required

- [ ] **Ignore:** Flexcom updates — no 2026 announcements from Wood Group; flexible pipe analysis remains specialized niche; track only if client demand appears

- [ ] **Ignore:** Sesam pricing — enterprise negotiated licensing; no public 2026 changes; competitively irrelevant at consultation pricing tier

---

## Summary of Week's Research Impact

This week's research reveals **three converging strategic inflection points** for workspace-hub:

### 1. Infrastructure Maturity Enables Cross-Vendor Skill Portability + Multi-Agent Reliability

The Agent Skills open standard (v0.9 published, v1.0 Q2 2026) + progressive disclosure (3-tier architecture) + SkillsBench/Braintrust regression evals create a **compounding improvement cycle** for skill quality:

- Skills written once work across Claude Code, Cursor, Gemini CLI, Codex CLI without modification
- Progressive disclosure reduces Phase 7 multi-agent context load by 40-60% (critical for dev-primary → licensed-win-1 coordination)
- Production failures (Phase 5 nightly researchers, Phase 7 smoke tests) feed regression suite → backsliding prevention → reliability compounds over time

**Actionable outcome:** Migrate `.claude/skills/` to SKILL.md spec by Q2 end, implement progressive disclosure with package-level scoping, design Phase 5/7 eval framework with 90%+ gate threshold.

### 2. Market Consolidation + Compute Commoditization Forces Value Anchor Shift: Traceability > Speed

Competitive intelligence confirms the strategic shift:

- SACS Cloud (Bentley Azure parallel, 10x speedup days→minutes, $13.3k/yr) commoditizes raw computation
- Offshore software market growing 7.4% CAGR ($750M→$818M 2025→2026) via strategic partnerships (DNV/Bentley/Ramboll/John Wood consolidation)
- Sesam (DNV) announced zero new modules 2026 H1 despite market growth
- Free/low-cost calculators (SkyCiv, TheNavalArch, CalcForge) apply margin pressure on generic tools

**aceengineer's sustainable differentiation:**

1. **Standards traceability** — calculation → DNV/API/ISO reference chain that commodity calculators lack
2. **Domain expertise** — VIV (unique to aceengineer), cathodic protection, DNV-RP-C203 2024 spectral fatigue
3. **Parametric design iteration** — systematic design space exploration (enabled by OrcaFlex 11.6c Python loads) vs. one-off analyses

Generic wall thickness/stability calculators face unsustainable margins at consultation pricing; shift focus to specialized domains.

**Actionable outcome:** Update PROJECT.md Key Decisions to document positioning rationale, audit aceengineer.com calculators for differentiation gaps, emphasize specialized domains in Phase 3 GTM copy.

### 3. Dependency Modernization (pandas 3.0, NumPy 2.4, uv 0.11.0, PyYAML CVE) Remains Table-Stakes for v1.1 Shipping

Prior week technical debt items (carried forward as high-priority):

- **pandas 3.0 Copy-on-Write** — affects Phase 1 (digitalmodel calculations) + Phase 2 (worldenergydata Parquet pipelines); grep for `df[...][...] = ` chained assignment across tier-1 repos
- **NumPy 2.4 generator deprecations** — `np.sum(generator)` → `np.fromiter()` refactor required; `np.round()` copy semantics validation
- **uv 0.11.0 TLS `--system-certs`** — test on all 4 machines, especially Phase 7 remote execution (dev-primary → licensed-win-1)
- **PyYAML CVE-2026-24009** — audit all `yaml.load()` for `SafeLoader`; if Phase 1.1 integrates external client YAML (OrcaFlex job files), add schema validation before deserialization
- **DNV-RP-C203 2024 S-N curves** — spectral fatigue module upgrade, benchmark L00–L06 delta, standards traceability update
- **ASME B31.4-2025 equation unification** — wall thickness module equivalence audit, low-temperature materials enable Arctic/subsea expansion (Phase 999.2)

**Actionable outcome:** Convert all 6 items to GitHub issues, prioritize for v1.1 gate before Phase 7 smoke tests ship.

---

**Cross-research convergence (2026-04-03 through 2026-04-10):**

- OrcaFlex 11.6c stability + Python variable loads validate Phase 7 automation feasibility
- SACS Cloud 10x speedup + market data ($818M 2026, 7.4% CAGR, strategic partnerships) quantify competitive pressure
- Sesam stasis + OpenFAST marine focus (not subsea risers) + Blue Kenue free licensing confirm no new direct OrcaFlex competitors
- pandas/NumPy/uv dependency modernization spans both completed phases (Phase 1 digitalmodel, Phase 2 worldenergydata) and upcoming Phase 7 — single audit unlocks both domains
- Agent Skills + progressive disclosure + regression evals create path to self-improving skill quality, directly applicable to Phase 5 (nightly researchers) + Phase 7 (solver verification)

**Net assessment:** The confluence of AI tooling maturity (Agent Skills, SkillsBench, hierarchical A2A delegation) + engineering software advances (OrcaFlex Python loads, ANSYS GPU, SACS Cloud parallel) + standards currency (DNV-RP-C203 2024, ASME B31.4-2025) creates an **automation-first workflow inflection point**. workspace-hub is well-positioned to capitalize: library-first digitalmodel strategy (Phase 6 decision), consultation-based pricing sustainable with specialized domain focus, and GSD framework already implements hierarchical delegation. The path forward: complete dependency modernization audit (pandas/NumPy/uv/PyYAML), migrate to Agent Skills v0.9 spec with progressive disclosure, design Phase 5/7 eval framework, and document competitive positioning rationale in PROJECT.md.
