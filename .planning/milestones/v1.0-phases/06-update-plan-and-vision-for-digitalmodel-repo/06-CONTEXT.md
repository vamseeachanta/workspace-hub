# Phase 6: Update plan and vision for digitalmodel repo - Context

**Gathered:** 2026-03-27 (updated)
**Status:** Ready for planning

<domain>
## Phase Boundary

Define the updated roadmap, architecture vision, and development priorities for the digitalmodel repo. Phase 1 shipped 3 new calculation modules, but the repo needs a refreshed plan reflecting current capabilities, market direction, and technical debt. UAT: Updated README/vision doc and roadmap committed to digitalmodel repo, priorities aligned with aceengineer.com GTM.

</domain>

<decisions>
## Implementation Decisions

### Vision Direction
- **D-01:** digitalmodel evolves as a **pip-installable Python engineering library**. Not a platform, not an API service. Direct imports by client projects and aceengineer.com.
- **D-02:** Primary consumers are Vamsee + client projects. aceengineer.com is the showcase. Not designing for open-source community contributions.
- **D-03:** Tier 2 agent API vision (from CALCULATIONS-VISION.md) stays as **aspirational future direction**, but not planned for now.
- **D-04:** Publish to **PyPI + GitHub**. assetutilities also published to PyPI for clean dependency chain.
- **D-05:** Follow **semver with deprecation** policy. Important for PyPI consumers.
- **D-06:** Keep **MIT license**. No dual licensing.
- **D-07:** Only **production-maturity modules** included in PyPI package. Experimental modules stay internal.
- **D-08:** Keep package name **digitalmodel**.
- **D-09:** Non-Python consumer support left to **Claude's discretion** based on architecture feasibility.

### Module Prioritization
- **D-10:** Client project needs drive which calculation modules get built next (carried from original D-01).
- **D-11:** Three **Tier 1 priorities**: (1) OrcaFlex/OrcaWave analysis automation, (2) cathodic protection module maturity, (3) parametric study generation pipeline.
- **D-12:** Parametric studies are a Tier 1 priority: digitalmodel generates parametric sweeps across standard calculations, outputs JSON data, aceengineer.com renders interactive JS charts as engineering lookup references for clients.
- **D-13:** Chart rendering: **Python generates JSON data, JavaScript renders** on aceengineer.com. No Python chart generation for web.

### Vision Doc & README
- **D-14:** **Trim CALCULATIONS-VISION.md** to essentials: vision statement, tier model, high-level stats. Detailed per-discipline tables stay in module-registry.yaml.
- **D-15:** **Trim README** to essentials: short description, install, quick example, link to docs. Professional, no emoji. PyPI-friendly.
- **D-16:** README **showcases standards traceability** as differentiator. Lead with "every calculation traces to its standard" messaging.
- **D-17:** Current docstring + YAML manifest documentation pattern is **sufficient**. No Sphinx/MkDocs needed.
- **D-18:** aceengineer.com calculators consume digitalmodel as the **engine**. Website never duplicates calculation logic.

### Tech Debt Priorities
- **D-19:** **Fix all 150 broken structural tests**. High priority, prerequisite for PyPI confidence.
- **D-20:** **Import path cleanup** to resolve test failures. Prerequisite for PyPI packaging.
- **D-21:** Identify a **prioritized subset** of the 455 standards gaps that matter for client work and aceengineer.com. Document which 20-50 gaps are actually valuable.
- **D-22:** **Refresh coverage metrics** — run coverage, update coverage.json, include current numbers in vision/roadmap docs.
- **D-23:** Keep **80% minimum coverage threshold** (already in pyproject.toml fail_under).
- **D-24:** Include a **dedicated PyPI-readiness milestone** in the roadmap: fix imports, fix tests, CI pipeline, publish.
- **D-25:** Add **GitHub Actions CI** to the roadmap. Tests + coverage on push/PR.
- **D-26:** **Formalize CHANGELOG.md** using Keep a Changelog format. Required for proper PyPI releases.

### OrcaFlex Scope
- **D-27:** OrcaFlex scope is **full pipeline**: `.yaml` high-level config → pure `.yaml` OrcaFlex input → external processing (pure `.yaml` → `.dat`, `.sim` → postprocess → summary → insights).
- **D-28:** Target **subsea pipelines/risers** first. Start with **1-2 canonical configurations** (e.g., static catenary riser, simple pipeline).
- **D-29:** **Standalone module** within digitalmodel/orcaflex/. Clean separation from structural analysis modules.
- **D-30:** **Include OrcaWave** (vessel hull analysis) in the Orca suite roadmap item. OrcaWave feeds vessel RAOs into OrcaFlex.
- **D-31:** Config format: **YAML configs**. Consistent with ASCII-first philosophy and existing digitalmodel patterns.
- **D-32:** Execution model: **generate locally, run on licensed Windows machine remotely**. No remote automation in initial scope.

### Roadmap Structure
- **D-33:** **Milestone-based format**, GSD-compatible with numbered phases. Same pattern as workspace-hub.
- **D-34:** Roadmap lives at **digitalmodel/ROADMAP.md** (repo root).
- **D-35:** **Self-contained** — no cross-references to workspace-hub phase numbers.
- **D-36:** **2-3 milestones** defined: M1=PyPI readiness (tests, imports, CI, publish), M2=Tier 1 modules (OrcaFlex + CP + parametric study infra), M3=next tier (TBD).
- **D-37:** **Dedicated parametric studies milestone** — not per-module work. Build the infrastructure first in M2.
- **D-38:** **Refresh module-registry.yaml maturity levels** to reflect post-Phase-1 state.

### Claude's Discretion
- Non-Python consumer architecture (API layer feasibility assessment)
- Exact milestone phase counts and phase ordering within each milestone
- Specific standards gaps to include in the prioritized subset (guided by client relevance)
- Module-registry.yaml schema updates if needed

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

### OrcaFlex/OrcaWave modules
- `digitalmodel/src/digitalmodel/orcaflex/` — Current OrcaFlex module (qa.py + reporting/)
- `digitalmodel/src/digitalmodel/orcawave/` — OrcaWave module directory

### GTM alignment
- `aceengineer-website/calculators/` — Existing calculator patterns that digitalmodel modules feed into
- `.planning/phases/03-gtm-and-marketing-aceengineer-website/03-CONTEXT.md` — Phase 3 GTM decisions

### Package configuration
- `digitalmodel/pyproject.toml` — Package config, dependencies, test config
- `digitalmodel/coverage.json` — Coverage data (Jan 2026, to be refreshed)
- `digitalmodel/CHANGELOG.md` — Changelog (to be formalized)
- `digitalmodel/README.md` — README (to be trimmed)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `CALCULATIONS-VISION.md` — Comprehensive current state audit (to be trimmed, not rewritten)
- `module-registry.yaml` — Already maps modules with maturity, capabilities, standards, and gaps (to be refreshed)
- `capability-report-2026-02-14.md` — Workspace-level capability assessment with maturity scores
- Existing calculator pattern on aceengineer.com — proven template for showcasing modules
- `orcaflex/qa.py` + `orcaflex/reporting/` — Starting point for OrcaFlex module expansion

### Established Patterns
- One-file-per-standard pattern for calculation modules
- Dual traceability: docstrings cite standards + YAML manifest for CI validation
- `assetutilities` as shared infrastructure dependency (both to be published to PyPI)
- `specs/` directory for module metadata and data needs
- YAML config-driven workflows (ASCII-first philosophy)

### Integration Points
- `module-registry.yaml` is the authority for module discovery — roadmap should reference it
- `data-needs.yaml` connects digitalmodel requirements to worldenergydata pipelines
- aceengineer.com calculators consume digitalmodel module capabilities via content sync
- Parametric study JSON output -> aceengineer.com JS chart rendering pipeline (new)

</code_context>

<specifics>
## Specific Ideas

- Parametric studies as rich charts on aceengineer.com: digitalmodel sweeps input ranges across standard calculations, outputs JSON, website renders interactive charts as engineering lookup references for clients
- OrcaFlex/OrcaWave bundled as "Orca suite" in roadmap — OrcaWave feeds vessel RAOs into OrcaFlex
- Standards traceability is the key differentiator for the README and PyPI listing
- Milestone ordering: PyPI readiness first (foundation), then Tier 1 modules with parametric infra, then expand

</specifics>

<deferred>
## Deferred Ideas

- OrcaFlex result extraction/post-processing — future milestone after model generation works
- Remote execution automation (SSH/job submission to licensed machine) — document manual workflow first
- Sphinx/MkDocs API documentation — revisit if community adoption demands it
- Module boundary review (digitalmodel vs assetutilities) — not in this phase, both publish to PyPI independently

</deferred>

---

*Phase: 06-update-plan-and-vision-for-digitalmodel-repo*
*Context gathered: 2026-03-27*
