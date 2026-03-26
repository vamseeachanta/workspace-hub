# Phase 6: Update plan and vision for digitalmodel repo - Context

**Gathered:** 2026-03-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Define the updated roadmap, architecture vision, and development priorities for the digitalmodel repo. Phase 1 shipped 3 new calculation modules, but the repo needs a refreshed plan reflecting current capabilities, market direction, and technical debt. UAT: Updated README/vision doc and roadmap committed to digitalmodel repo, priorities aligned with aceengineer.com GTM.

</domain>

<decisions>
## Implementation Decisions

### Module Prioritization
- **D-01:** Client project needs drive which calculation modules get built next — not standards coverage breadth or website calculator demand alone.
- **D-02:** No single domain dominance — each client project pulls from different modules (subsea, structural, hydrodynamics, etc.). Prioritize by whichever project is most imminent.
- **D-03:** Use lightweight tiers for prioritization: Tier 1 (build next), Tier 2 (build when needed), Tier 3 (backlog). Re-tier as new client projects arrive.
- **D-04:** aceengineer.com calculator needs are a secondary signal — modules that also make good calculators get a small boost but don't override client demand.
- **D-05:** Two specific modules are Tier 1 priorities for the roadmap: (1) OrcaFlex analysis for subsea structures — advancing the existing OrcaFlex integration into a production-grade subsea structural analysis workflow, and (2) cathodic protection module maturity — elevating the existing CP module (3 standard implementations: API RP 1632, DNV-RP-B401, ISO 15589-2) to higher maturity with improved test coverage and any missing standard coverage.

### Claude's Discretion
- Vision direction: whether digitalmodel should evolve as a library, platform, API, or hybrid — determine based on current architecture and practical constraints
- Tech debt scope: how deep the audit goes (catalog issues vs. propose architecture changes). Known issues: 0/150 structural tests runnable, 455 standards gaps, coverage.json from Jan 2026
- Roadmap format: milestone-based, module-by-module, quarterly, or tied to aceengineer.com releases — choose what fits a solo engineer's workflow
- Roadmap granularity: how many phases/milestones to define in the digitalmodel repo's own roadmap

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Current state documentation
- `digitalmodel/docs/vision/CALCULATIONS-VISION.md` — Current ecosystem state: 7,355 functions, 42 standards done, 455 gaps across 30 disciplines
- `digitalmodel/docs/capability-map/capability-report-2026-02-14.md` — Workspace capability report with maturity ratings
- `digitalmodel/specs/module-registry.yaml` — Master registry of all modules, maturity levels, and documented gaps
- `digitalmodel/specs/data-needs.yaml` — Structured lifecycle tracking for data dependencies

### Phase 1 outputs (context for what was already built)
- `digitalmodel/src/digitalmodel/cathodic_protection/dnv_rp_b401.py` — Reference implementation of one-file-per-standard pattern
- `digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_codes/` — Multi-standard wall thickness implementations
- `digitalmodel/tests/structural/analysis/TEST_STATUS_DASHBOARD.md` — Documents 0/150 runnable tests

### GTM alignment
- `aceengineer-website/calculators/` — Existing calculator patterns that new digitalmodel modules could feed into
- `.planning/phases/03-gtm-and-marketing-aceengineer-website/03-CONTEXT.md` — Phase 3 GTM decisions

### Package configuration
- `digitalmodel/pyproject.toml` — Package config, dependencies, test config
- `digitalmodel/coverage.json` — Coverage data (Jan 2026)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `CALCULATIONS-VISION.md` — Comprehensive current state audit (can be updated rather than rewritten)
- `module-registry.yaml` — Already maps modules with maturity, capabilities, standards, and gaps
- `capability-report-2026-02-14.md` — Workspace-level capability assessment with maturity scores
- Existing calculator pattern on aceengineer.com — proven template for showcasing modules

### Established Patterns
- One-file-per-standard pattern for calculation modules
- Dual traceability: docstrings cite standards + YAML manifest for CI validation
- `assetutilities` as shared infrastructure dependency
- `specs/` directory for module metadata and data needs

### Integration Points
- `module-registry.yaml` is the authority for module discovery — roadmap should reference it
- `data-needs.yaml` connects digitalmodel requirements to worldenergydata pipelines
- aceengineer.com calculators consume digitalmodel module capabilities via content sync

</code_context>

<specifics>
## Specific Ideas

- OrcaFlex analysis for subsea structures and cathodic protection module maturity are the two explicitly named Tier 1 priorities
- Module prioritization must be responsive to client project arrivals, not locked to a static list
- These two modules likely serve both client needs and demonstrate platform capabilities on aceengineer.com

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 06-update-plan-and-vision-for-digitalmodel-repo*
*Context gathered: 2026-03-26*
