# Phase 6: Update Plan and Vision for digitalmodel Repo - Research

**Researched:** 2026-03-26
**Domain:** Engineering software library strategy, roadmap documentation, Python package planning
**Confidence:** HIGH

## Summary

Phase 6 is a documentation and strategy phase, not a code implementation phase. The deliverables are updated vision documents and an actionable roadmap committed to the digitalmodel repo itself. The repo already has substantial current-state documentation: `CALCULATIONS-VISION.md` (ecosystem state audit), `module-registry.yaml` (1,569-line structured module catalog), `capability-report-2026-02-14.md` (workspace capability assessment), and `data-needs.yaml` (lifecycle data tracking). The primary work is synthesizing these into a coherent forward-looking vision and roadmap, not auditing from scratch.

The two locked Tier 1 priorities (OrcaFlex subsea structural analysis, cathodic protection maturity) are well-grounded in existing code: the OrcaFlex integration already has model generation, run automation, and post-processing (`solvers/orcaflex/`), and the CP module has 4 implementation files with 72 passing tests across 3 standards. The roadmap must define what "production-grade" and "higher maturity" mean concretely for each.

**Primary recommendation:** Structure the roadmap as a tiered module-by-module progression (Tier 1/2/3) with milestones tied to client project arrivals, updating `CALCULATIONS-VISION.md` as the living vision document and adding a new `ROADMAP.md` at the digitalmodel repo root. Do not create an elaborate multi-document system -- a solo engineer needs one vision doc and one roadmap file.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Client project needs drive which calculation modules get built next -- not standards coverage breadth or website calculator demand alone.
- **D-02:** No single domain dominance -- each client project pulls from different modules (subsea, structural, hydrodynamics, etc.). Prioritize by whichever project is most imminent.
- **D-03:** Use lightweight tiers for prioritization: Tier 1 (build next), Tier 2 (build when needed), Tier 3 (backlog). Re-tier as new client projects arrive.
- **D-04:** aceengineer.com calculator needs are a secondary signal -- modules that also make good calculators get a small boost but don't override client demand.
- **D-05:** Two specific modules are Tier 1 priorities for the roadmap: (1) OrcaFlex analysis for subsea structures -- advancing the existing OrcaFlex integration into a production-grade subsea structural analysis workflow, and (2) cathodic protection module maturity -- elevating the existing CP module (3 standard implementations: API RP 1632, DNV-RP-B401, ISO 15589-2) to higher maturity with improved test coverage and any missing standard coverage.

### Claude's Discretion
- Vision direction: whether digitalmodel should evolve as a library, platform, API, or hybrid -- determine based on current architecture and practical constraints
- Tech debt scope: how deep the audit goes (catalog issues vs. propose architecture changes). Known issues: 0/150 structural tests runnable, 455 standards gaps, coverage.json from Jan 2026
- Roadmap format: milestone-based, module-by-module, quarterly, or tied to aceengineer.com releases -- choose what fits a solo engineer's workflow
- Roadmap granularity: how many phases/milestones to define in the digitalmodel repo's own roadmap

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.
</user_constraints>

## Standard Stack

This phase produces documentation, not code. The "stack" is the set of existing documentation files and formats already established in the digitalmodel repo.

### Core Deliverable Files
| File | Location | Purpose | Status |
|------|----------|---------|--------|
| CALCULATIONS-VISION.md | `docs/vision/` | Ecosystem current state + tier progression + gap register | EXISTS -- update, don't rewrite |
| ROADMAP.md | repo root | Actionable tiered roadmap with milestones | CREATE NEW |
| module-registry.yaml | `specs/` | Structured module catalog with maturity levels | EXISTS -- update maturity levels |
| README.md | repo root | High-level project description with vision section | EXISTS -- update vision section |

### Supporting Files (reference only, do not rewrite)
| File | Location | Purpose | Status |
|------|----------|---------|--------|
| capability-report-2026-02-14.md | `docs/capability-map/` | Workspace-level capability assessment | EXISTS -- reference |
| data-needs.yaml | `specs/` | Data dependency lifecycle tracker | EXISTS -- reference |
| pyproject.toml | repo root | Package config, test config | EXISTS -- reference for tech debt |
| TEST_STATUS_DASHBOARD.md | `tests/structural/analysis/` | Documents 0/150 test failures | EXISTS -- reference for tech debt |

### No Installation Required
This phase writes markdown and YAML. No package installations needed.

## Architecture Patterns

### Recommended Document Structure

The digitalmodel repo should have this documentation layout after Phase 6:

```
digitalmodel/
  ROADMAP.md                    # NEW: Tiered roadmap with milestones
  README.md                     # UPDATED: Refreshed vision section
  docs/
    vision/
      CALCULATIONS-VISION.md    # UPDATED: Current state + gap register + tier progression
  specs/
    module-registry.yaml        # UPDATED: Maturity levels refreshed
```

### Pattern 1: Tiered Module Prioritization

**What:** Three-tier system (D-03) where modules move between tiers as client projects arrive.
**When to use:** Every prioritization decision in the roadmap.

```markdown
## Tier 1: Build Next
Modules actively needed for current/imminent client projects.

### OrcaFlex Subsea Structural Analysis
- Current state: [what exists]
- Target state: [what production-grade means]
- Gaps: [specific work items]
- Estimated effort: [person-days]

### Cathodic Protection Maturity
- Current state: [what exists]
- Target state: [what higher maturity means]
- Gaps: [specific work items]
- Estimated effort: [person-days]

## Tier 2: Build When Needed
Modules with partial implementations that will be completed when a client project requires them.

## Tier 3: Backlog
Modules with known gaps but no current client demand. Re-tier as projects arrive.
```

### Pattern 2: Vision as Direction, Not Specification

**What:** The vision document should state what digitalmodel IS (library with CLI tooling, not a platform or SaaS), what it DOES (calculations traceable to standards), and where it's GOING (Tier 1 -> Tier 2 -> Tier 3 progression). It should NOT be a detailed specification.
**When to use:** When writing/updating CALCULATIONS-VISION.md.

**Recommended vision direction:** Based on current architecture analysis:
- digitalmodel is a **Python library with CLI entry points** (27 CLI commands registered in pyproject.toml)
- It is NOT a platform (no web server, no user management, no database)
- It is NOT an API service (FastAPI is in dependencies but appears unused for the core calculation workflow)
- The aceengineer-website consumes it via content sync and JavaScript reimplementations, not via API calls
- **Recommendation:** Vision should position digitalmodel as a **library-first** package: importable Python calculations with CLI convenience wrappers, feeding into client project reports and aceengineer.com showcase calculators

### Pattern 3: Tech Debt as Actionable Catalog

**What:** Document tech debt as specific, actionable items rather than vague architectural concerns. Each item gets: what's wrong, impact, fix effort estimate.
**When to use:** When writing the tech debt section of the roadmap.

Known tech debt items from audit:
1. **0/150 structural tests runnable** -- 3 import path issues blocking all marine_engineering tests (TEST_STATUS_DASHBOARD.md, Oct 2025, likely still unfixed)
2. **455 standards gaps** in capability map -- many are aspirational, not actual code gaps
3. **Bloated pyproject.toml** -- 170+ dependencies including irrelevant packages (celery, redis, newrelic, gunicorn, boto3, fastapi) that have nothing to do with engineering calculations
4. **coverage.json from Jan 2026** -- 5 months stale
5. **Duplicate module paths** -- catenary solver exists in subsea/catenary (stub), subsea/catenary_riser, marine_ops/marine_analysis, and marine_ops/marine_engineering
6. **No VISION.md at repo root** -- CALCULATIONS-VISION.md exists but ecosystem VISION.md referenced in it does not
7. **pyproject.toml version mismatch** -- `version = "0.1.1"` but README says "Version: 3.0.0"
8. **Stub modules with no value** -- specialized/digitalmarketing, specialized/finance, specialized/project_management are stubs cluttering the namespace

### Anti-Patterns to Avoid
- **Over-planning:** Do not create a 6-month detailed sprint plan for a solo engineer. Keep milestones event-driven (client project arrivals), not calendar-driven.
- **Rewriting existing docs:** CALCULATIONS-VISION.md is comprehensive. Update it, don't replace it.
- **Vision inflation:** Do not promise platform/SaaS/API features. The repo is a calculation library. Keep the vision honest.
- **Static roadmap:** The roadmap MUST be designed to be re-tiered. Avoid fixed "Q1/Q2/Q3" milestones.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Roadmap tracking | Custom issue tracker or database | GitHub Issues + ROADMAP.md tiers | Already have 50+ open issues; GitHub Issues is the tracker |
| Module discovery | Custom registry format | Existing module-registry.yaml (YAML) | Already 1,569 lines, well-structured, machine-readable |
| Test health tracking | Custom dashboard system | pytest output + TEST_STATUS_DASHBOARD.md pattern | Already established pattern |
| Standards gap tracking | Custom database | CALCULATIONS-VISION.md gap register | Already comprehensive; 455 gaps cataloged |

**Key insight:** The digitalmodel repo already has extensive metadata infrastructure. This phase updates and connects existing documents, not creates new systems.

## Common Pitfalls

### Pitfall 1: Conflating Vision with Current State
**What goes wrong:** The vision document becomes a catalog of what exists rather than a direction statement.
**Why it happens:** CALCULATIONS-VISION.md currently mixes current state tables with tier progression targets. Easy to just add more tables.
**How to avoid:** Separate the document into clear sections: "Current State" (factual), "Vision" (directional), "Roadmap" (actionable). Or better: keep current state in CALCULATIONS-VISION.md, put the forward-looking roadmap in ROADMAP.md.
**Warning signs:** If the "vision" section has more tables than paragraphs, it's become a status report.

### Pitfall 2: Roadmap That Cannot Be Updated
**What goes wrong:** Roadmap uses fixed dates or sequential phase numbers that become stale within weeks.
**Why it happens:** Natural instinct to create structured timelines. But for a solo engineer responding to client projects, the next priority can change overnight.
**How to avoid:** Use tiers (D-03), not timelines. Each module is in a tier. Tiers are re-evaluated when a new client project arrives. This is explicitly what the user decided.
**Warning signs:** Calendar dates in the roadmap. Sequential "Phase 1, Phase 2" numbering that implies ordering.

### Pitfall 3: Ignoring the GTM Connection
**What goes wrong:** Roadmap focuses purely on engineering modules without connecting to aceengineer.com calculator opportunities.
**Why it happens:** Engineering focus naturally gravitates toward standards coverage rather than marketing signal.
**How to avoid:** For each Tier 1/2 module, note whether it has calculator potential (D-04). The aceengineer.com site already has 5 calculators (fatigue-life, fatigue-sn-curve, npv-field-development, on-bottom-stability, wall-thickness). New modules that make good calculators get a priority boost.
**Warning signs:** No mention of aceengineer.com in the roadmap.

### Pitfall 4: Tech Debt Without Triage
**What goes wrong:** Tech debt section becomes a dump of every issue, making it feel overwhelming.
**Why it happens:** 455 standards gaps, 150 broken tests, bloated dependencies -- easy to list everything.
**How to avoid:** Triage tech debt into: (a) blocks current work, (b) degrades developer experience, (c) aspirational. Only (a) and (b) belong in the roadmap. Category (c) goes in a backlog.
**Warning signs:** Tech debt section longer than the rest of the roadmap combined.

### Pitfall 5: README Scope Creep
**What goes wrong:** README becomes a 650-line document (current state) that no one reads.
**Why it happens:** Each new module gets its own README section. The current README is already 650 lines.
**How to avoid:** README should be a concise entry point: what is this, how to install, where to learn more. Module details belong in module-level docs or the registry. The vision update should trim the README, not expand it.
**Warning signs:** README exceeds 200 lines.

## Code Examples

This phase does not produce code. The deliverables are markdown and YAML. Below are structural examples.

### Example: ROADMAP.md Structure
```markdown
# digitalmodel Roadmap

> Tethering timeless engineering to a single source of truth.

## How This Roadmap Works

Modules are tiered by client project demand (Tier 1: build next, Tier 2: build when needed,
Tier 3: backlog). Tiers are re-evaluated when new client projects arrive. aceengineer.com
calculator potential is a secondary signal.

## Tier 1: Active Development

### OrcaFlex Subsea Structural Analysis
**Current:** Model generation, run automation, post-processing exist in solvers/orcaflex/
**Target:** Production-grade subsea structural analysis workflow
**Work remaining:**
- [ ] Define subsea analysis template (jacket, pipeline, riser scenarios)
- [ ] Validate against reference project results
- [ ] Add integration tests for end-to-end workflow
**Calculator potential:** Medium (complex workflows don't simplify to web calculators)

### Cathodic Protection Maturity
**Current:** 4 implementations (DNV-RP-B401, API RP 1632, ISO 15589-2, fuel system CP), 72 tests
**Target:** Higher maturity with improved test coverage, missing standard coverage
**Work remaining:**
- [ ] Identify missing standard clauses within implemented standards
- [ ] Add worked-example tests from standard appendices
- [ ] Add ABS GN Ships/Offshore full implementation (currently "configured" only)
- [ ] Update module-registry.yaml maturity from "development" to "production"
**Calculator potential:** High (CP sizing is a natural web calculator)

## Tier 2: Build When Needed
[modules with partial implementations]

## Tier 3: Backlog
[modules with known gaps but no current demand]

## Tech Debt
[triaged list of debt items]
```

### Example: Updated CALCULATIONS-VISION.md Sections
```markdown
## Vision Direction

digitalmodel is a Python calculation library: importable functions with CLI wrappers,
each traceable to an international engineering standard. It feeds into:
1. Client project analysis reports (direct Python usage)
2. aceengineer.com interactive calculators (JavaScript reimplementations)
3. Future agent-based engineering workflows (Tier 2/3 capability)

### What digitalmodel is NOT
- Not a platform or SaaS product
- Not a web API (though one could be built on top)
- Not a monolithic application
```

## Document Intelligence as Input Pipeline

The workspace-hub has a comprehensive document intelligence platform that feeds directly into digitalmodel modules. The vision and roadmap must account for this as a primary data source.

### What Exists
| Component | Location | Scale | Purpose |
|-----------|----------|-------|---------|
| Corpus index | `data/document-index/index.jsonl` | 1,033,933 docs | Master document catalog with domain, readability, org |
| Extraction indexes | `data/doc-intelligence/*.jsonl` | 6 content types | constants (4.9 MB), equations (2.0 MB), requirements (12 MB), definitions, procedures, worked examples |
| Deep extraction reports | `data/doc-intelligence/deep/` | 9+ major standards | Per-standard YAML manifests (API 579-1, DNV RP series, ISO standards) |
| Promoted tables | `data/doc-intelligence/promoted-tables/` | CSV artifacts | Tables extracted and promoted from standards for direct code use |
| Naval architecture catalog | `data/doc-intelligence/naval-architecture-catalog.yaml` | 144 docs | 110 ship plans, 21 textbooks, 65 hull codes |
| Standards transfer ledger | `data/document-index/standards-transfer-ledger.yaml` | 425 standards | Maps standards → target repos/modules |

### Pipeline Architecture (7-phase)
- Phase A: Corpus scan → index.jsonl (1M+ records)
- Phase B: LLM extraction + classification (Claude CLI worker)
- Phase C: Domain classification
- Phase D: Data source specs
- Phase E: Backfill index fields
- Phase F-G: Enrichment and readability assessment

### How It Feeds digitalmodel
1. **Reference data for calculations:** Extracted constants, equations, and procedures from engineering standards become inputs to digitalmodel calculation modules (e.g., CP design parameters from DNV-RP-B401)
2. **Test fixtures:** Worked examples extracted from standards serve as TDD test cases for calculation implementations (e.g., 82 naval architecture worked examples)
3. **Gap identification:** The standards-transfer-ledger maps 425 standards to target repos — digitalmodel's 455 standards gaps should cross-reference this ledger
4. **Module validation:** Deep extraction reports contain reference values that can validate calculation module outputs
5. **Maturity signal:** Extraction yield metrics (69-93% for tables, 0% for equations/constants via text) inform which modules have sufficient reference data to implement

### Key Metrics for Roadmap
| Metric | Value | Relevance to digitalmodel |
|--------|-------|--------------------------|
| Standards with promoted data | 3 (DNV-RP-B401, DNV-RP-C203, DNV-RP-F109) | These 3 are ready for direct code promotion |
| Extraction readiness | 96.7% of corpus | Most documents classifiable for domain routing |
| Table yield | 69-93% | Tables are the reliable extraction target |
| Equation yield | 0% | Cannot automate equation extraction — manual reference needed |
| Worked examples | 82 (naval arch) | Below 150-200 target; gap in textbook problem sets |

### Implications for Vision/Roadmap
- The roadmap should reference document intelligence as the **upstream data pipeline** for new calculation modules
- Tier 1 modules (OrcaFlex, CP) should note which doc-intelligence artifacts already exist to support them
- The vision should acknowledge the extraction→promotion→implementation workflow as the standard path for new modules
- Tech debt audit should check whether module-registry.yaml `data_sources` fields align with doc-intelligence extraction status
- `data-needs.yaml` in digitalmodel/specs/ tracks lifecycle data dependencies — roadmap should connect these to doc-intelligence delivery status

### Scripts & Skills to Reference
| Tool | Path | Purpose |
|------|------|---------|
| doc-extraction skill | `.claude/skills/engineering/doc-extraction/SKILL.md` | Main extraction workflow with domain sub-skills |
| doc-intelligence-promotion skill | `.claude/skills/data/doc-intelligence-promotion/SKILL.md` | Tables→CSV, equations→Python, procedures→YAML |
| document-index-pipeline skill | `.claude/skills/data/document-index-pipeline/SKILL.md` | 7-phase batch indexing orchestration |
| Platform design spec | `docs/superpowers/specs/2026-03-12-doc-intelligence-platform-design.md` | Architecture: extraction manifest schema, federated indexes, promotion pipeline |
| Data intelligence map | `docs/document-intelligence/data-intelligence-map.md` | Registry of all data intelligence artifacts |

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Monolithic README with all module details | Module-registry.yaml + focused README | Feb 2026 | Machine-readable discovery, but README still bloated |
| WRK-* work items in workspace-hub | GitHub Issues as primary tracker | Mar 2026 (GSD migration) | Issues now the canonical work tracker |
| Sprint-based roadmapping | Event-driven tiering (D-03) | Mar 2026 (this phase) | Solo engineer workflow, responsive to client arrivals |

**Deprecated/outdated:**
- WRK-* numbered work items: replaced by GitHub Issues (GSD migration completed 2026-03-25)
- Sprint-based planning: replaced by tier-based prioritization per user decisions

## Existing Assets Inventory

### What Already Exists (DO NOT RECREATE)

| Asset | Path | Lines | Last Updated | Quality |
|-------|------|-------|--------------|---------|
| CALCULATIONS-VISION.md | docs/vision/ | 243 | ~Feb 2026 (WRK-1179 sprint) | High -- comprehensive current state, gap register, tier definitions |
| module-registry.yaml | specs/ | 1,569 | Feb 2026 | High -- structured YAML, all modules cataloged with maturity/gaps/standards |
| capability-report-2026-02-14.md | docs/capability-map/ | 100+ | Feb 2026 | Medium -- workspace-level, useful context |
| data-needs.yaml | specs/ | 80+ | Mar 2026 | High -- lifecycle tracking for data dependencies |
| README.md | repo root | 650 | Mar 2026 | Low -- bloated, outdated stats, emoji-heavy |
| CHANGELOG.md | repo root | 60+ | Oct 2025 | Medium -- last entry is v2.0.0, no entries for Phase 1 sprint work |
| TEST_STATUS_DASHBOARD.md | tests/structural/analysis/ | 451 | Oct 2025 | Medium -- documents real problem, but likely stale |
| pyproject.toml | repo root | 405 | Recent | Low -- dependency bloat, version mismatch |

### Current Module Maturity Summary (from module-registry.yaml)

| Maturity Level | Count | Examples |
|----------------|-------|---------|
| production | ~5 | structural/fatigue, structural/analysis, hydrodynamics, hydrodynamics/diffraction, hydrodynamics/aqwa |
| stable | ~15 | structural/structural_analysis, subsea/pipeline, subsea/mooring_analysis, asset_integrity, etc. |
| beta | ~6 | subsea/vertical_riser, marine_ops/reservoir, marine_ops/ct_hydraulics, etc. |
| development | ~2 | subsea/on_bottom_stability, etc. |
| stub | ~4 | subsea/catenary, specialized/digitalmarketing, specialized/finance, specialized/project_management |

### Current Calculator Alignment

| aceengineer.com Calculator | digitalmodel Module | Alignment |
|---------------------------|---------------------|-----------|
| fatigue-life-calculator | structural/fatigue | Direct -- S-N curves + damage accumulation |
| fatigue-sn-curve | structural/fatigue | Direct -- 221 S-N curves from 17 standards |
| npv-field-development | (worldenergydata) | Cross-repo -- NPV/MIRR with carbon cost |
| on-bottom-stability | subsea/on_bottom_stability | Direct -- DNV-RP-F109 |
| wall-thickness | structural/analysis | Direct -- ASME B31.4 wall thickness |

**Gap opportunity for next calculators:** Cathodic protection sizing (CP module has 72 tests, 3 standards), mooring line design, VIV screening.

## Open Questions

1. **What does "production-grade OrcaFlex subsea analysis" mean concretely?**
   - What we know: OrcaFlex integration exists (model generation, run automation, post-processing). The module has 20+ files in `solvers/orcaflex/`.
   - What's unclear: Whether "production-grade" means (a) better test coverage for existing code, (b) new analysis templates for common scenarios, (c) validation against reference projects, or (d) all of the above.
   - Recommendation: The planner should define "production-grade" as: (1) at least 3 reference scenario templates (jacket, pipeline, riser), (2) integration tests running without OrcaFlex license, (3) validated output against at least 1 real project result.

2. **Should the README be trimmed?**
   - What we know: Current README is 650 lines with detailed module descriptions that duplicate the registry.
   - What's unclear: Whether the user values the comprehensive README or would prefer a concise one.
   - Recommendation: Trim to ~150 lines (installation, vision, quick example, link to docs). Module details live in module-registry.yaml and per-module docs.

3. **How to handle the 455 standards gaps?**
   - What we know: 455 gaps are cataloged in CALCULATIONS-VISION.md. Many are aspirational (entire disciplines not yet started).
   - What's unclear: How to present this in a roadmap without it feeling overwhelming.
   - Recommendation: Only include gaps relevant to Tier 1 and Tier 2 modules in the roadmap. Keep the full 455-gap register in CALCULATIONS-VISION.md as reference.

4. **CHANGELOG.md currency**
   - What we know: Last CHANGELOG entry is v2.0.0 from Oct 2025. Phase 1 sprint work (cathodic protection, wall thickness codes, on-bottom stability) is not recorded.
   - What's unclear: Whether updating CHANGELOG is in scope for Phase 6 or should be deferred.
   - Recommendation: Include a CHANGELOG update task -- it takes 15 minutes and signals active development.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 7.4+ (configured in pyproject.toml) |
| Config file | `pyproject.toml` [tool.pytest.ini_options] + `pytest.ini` |
| Quick run command | `cd digitalmodel && python -m pytest tests/ -x --tb=short -q` |
| Full suite command | `cd digitalmodel && python -m pytest tests/ --tb=short` |

### Phase Requirements -> Test Map

This phase produces documentation, not code. Validation is UAT-based (human review), not test-based.

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| P6-01 | Updated CALCULATIONS-VISION.md reflects current state | manual-only | N/A -- human review of document accuracy | N/A |
| P6-02 | ROADMAP.md uses tier-based prioritization per D-03 | manual-only | N/A -- structural review | N/A |
| P6-03 | Tier 1 lists OrcaFlex + CP per D-05 | manual-only | `grep -c "Tier 1" digitalmodel/ROADMAP.md` (existence check only) | N/A |
| P6-04 | Tech debt documented with triage | manual-only | N/A -- human review | N/A |
| P6-05 | README updated with refreshed vision | manual-only | N/A -- human review | N/A |
| P6-06 | module-registry.yaml maturity levels current | manual-only | N/A -- human review against actual module state | N/A |

### Sampling Rate
- **Per task commit:** Visual review of changed files
- **Per wave merge:** Cross-reference ROADMAP.md tiers against module-registry.yaml maturity levels
- **Phase gate:** All 4 deliverable files updated and committed; priorities aligned with aceengineer.com GTM

### Wave 0 Gaps
None -- this phase produces documentation, not code. No test infrastructure needed.

## Project Constraints (from CLAUDE.md)

- Retrieval first -- consult `docs/`, `.claude/docs/`, `.claude/rules/`, memory before training knowledge
- Workflow: GSD framework
- Edit safety: prefer targeted single-site edits over bulk find-replace
- Agent harness files (CLAUDE.md, MEMORY.md, etc.) must not exceed 20 lines -- not relevant for this phase's deliverables
- Path handling: use relative paths in scripts, absolute only when tool calls require them

## Sources

### Primary (HIGH confidence)
- `digitalmodel/docs/vision/CALCULATIONS-VISION.md` -- comprehensive current state, gap register, 243 lines
- `digitalmodel/specs/module-registry.yaml` -- 1,569-line module catalog with maturity/gaps/standards
- `digitalmodel/README.md` -- 650-line current README
- `digitalmodel/pyproject.toml` -- 405-line package config
- `digitalmodel/tests/structural/analysis/TEST_STATUS_DASHBOARD.md` -- 451-line test status documenting 0/150 runnable tests
- `digitalmodel/docs/capability-map/capability-report-2026-02-14.md` -- workspace capability assessment
- `.planning/phases/06-update-plan-and-vision-for-digitalmodel-repo/06-CONTEXT.md` -- user decisions

### Secondary (MEDIUM confidence)
- `aceengineer-website/calculators/` -- 5 calculators (3 original + 2 from Phase 3)
- `.planning/phases/03-gtm-and-marketing-aceengineer-website/03-CONTEXT.md` -- GTM decisions
- `digitalmodel/CHANGELOG.md` -- last entry Oct 2025
- GitHub Issues -- 50+ open issues in digitalmodel repo
- `data/document-index/index.jsonl` -- 1M+ document corpus index
- `data/doc-intelligence/*.jsonl` -- extracted constants, equations, requirements, procedures, definitions, worked examples
- `data/document-index/standards-transfer-ledger.yaml` -- 425 standards → repo/module mapping
- `docs/superpowers/specs/2026-03-12-doc-intelligence-platform-design.md` -- doc-intelligence platform architecture
- `docs/document-intelligence/data-intelligence-map.md` -- data intelligence artifact registry

### Tertiary (LOW confidence)
- Module maturity assessments in module-registry.yaml may be stale (generated Feb 2026, some modules may have changed)
- Test counts from CALCULATIONS-VISION.md are from WRK-1179 sprint and may not reflect current state

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- deliverable files are well-established, no new tooling needed
- Architecture: HIGH -- document structure follows existing patterns in the repo
- Pitfalls: HIGH -- drawn directly from analysis of existing documents and user decisions
- Vision direction: MEDIUM -- recommendation to stay library-first is based on architecture analysis, but user has final say (Claude's discretion area)
- Tech debt catalog: MEDIUM -- based on snapshot analysis; some items may have been fixed since dashboards were written

**Research date:** 2026-03-26
**Valid until:** 2026-04-26 (30 days -- documentation strategy is stable)
