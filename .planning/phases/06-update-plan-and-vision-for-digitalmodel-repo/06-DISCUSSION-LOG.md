# Phase 6: Update plan and vision for digitalmodel repo - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-27 (updated from 2026-03-26)
**Phase:** 06-update-plan-and-vision-for-digitalmodel-repo
**Areas discussed:** Vision direction, Tech debt priorities, OrcaFlex scope, Roadmap structure

---

## Previous Session (2026-03-26): Module Prioritization

### What should drive which calculation modules get built next?

| Option | Description | Selected |
|--------|-------------|----------|
| aceengineer.com calculator demand | Prioritize modules that become interactive calculators on the website | |
| Client project needs | Build modules that directly serve active or anticipated client engagements | ✓ |
| Standards coverage gaps | Systematically close the 455 standards gaps in the capability map | |

**User's choice:** Client project needs
**Notes:** Direct revenue pull — build what clients need.

### Specific engineering domains?

| Option | Description | Selected |
|--------|-------------|----------|
| Subsea engineering focus | Pipeline, riser, VIV, on-bottom stability | |
| Structural analysis focus | Fatigue, buckling, wall thickness, member capacity | |
| Mixed — project-dependent | No single domain dominance, prioritize by imminent project | ✓ |

**User's choice:** Mixed — project-dependent
**Notes:** Each client project pulls from different modules.

### Prioritization framework?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — scoring system | Define criteria with weights, re-rank quarterly | |
| Yes — lightweight tiers | Tier 1/2/3 grouping, re-tier as projects arrive | ✓ |
| No — just a prioritized list | Manual ranking, update when priorities shift | |

**User's choice:** Yes — lightweight tiers
**Notes:** Tier 1 (build next), Tier 2 (build when needed), Tier 3 (backlog).

### How should aceengineer.com needs factor in?

| Option | Description | Selected |
|--------|-------------|----------|
| Secondary signal | Client needs first, calculator-ready modules get small boost | ✓ |
| Equal weight | Modules serving both client + calculator needs get priority | |
| You decide | Claude's discretion | |

**User's choice:** Secondary signal
**Notes:** Doesn't override client demand.

### Specific modules added (user-initiated)

**User's input:** "I would like to add OrcaFlex analysis for subsea structures and cathodic protection module maturity — these 2 particular modules"
**Result:** Added as explicit Tier 1 priorities.

---

## Updated Session (2026-03-27): Vision Direction

### What should digitalmodel evolve into?

| Option | Description | Selected |
|--------|-------------|----------|
| Engineering library | Pip-installable Python package. Clients import directly. | ✓ |
| API service | REST/gRPC wrapper. More infra overhead. | |
| Library + thin API layer | Library first, optional FastAPI wrapper. | |
| Platform with agent routing | Agent API, NL routing, report templates. | |

**User's choice:** Engineering library
**Notes:** Simplest path for solo engineer.

### Tier 2 Vision

| Option | Description | Selected |
|--------|-------------|----------|
| Keep as aspirational | Leave in vision doc as future direction | ✓ |
| Remove it | Strip from vision docs | |
| Defer to backlog | Move to backlog item | |

### Primary Consumers

| Option | Description | Selected |
|--------|-------------|----------|
| You + client projects | Own engineering work and client deliverables | ✓ |
| Open-source community | External contributors, public API stability | |
| Both equally | Internal-driven, public API discipline | |

### Distribution

| Option | Description | Selected |
|--------|-------------|----------|
| GitHub + PyPI | Standard open-source distribution | ✓ |
| GitHub only | Git URL install, simpler | |
| Private PyPI + GitHub | Private index for clients | |

### API Stability

| Option | Description | Selected |
|--------|-------------|----------|
| Semver with deprecation | Follow semver, deprecate before removing | ✓ |
| Move fast, break things | No stability promises | |
| Stable per-module | Mature modules stable, others break freely | |

### Documentation Standard

| Option | Description | Selected |
|--------|-------------|----------|
| Current is fine | Docstring + YAML manifest sufficient | ✓ |
| Add Sphinx/MkDocs | API docs from docstrings | |
| Add usage examples | Worked examples per module | |

### Vision Doc Structure

| Option | Description | Selected |
|--------|-------------|----------|
| Trim to essentials | Keep vision + stats, cut per-discipline tables | ✓ |
| Keep as-is | Audit-style useful for scope | |
| Split into two files | Vision + Audit separate | |

### Website Relationship

| Option | Description | Selected |
|--------|-------------|----------|
| digitalmodel is the engine | Website consumes, never duplicates logic | ✓ |
| Independent implementations | Website JS standalone | |
| Validation source | Reference values for validation | |

### Non-Python Consumers

| Option | Description | Selected |
|--------|-------------|----------|
| You decide | Claude's discretion | ✓ |

### assetutilities Dependency

| Option | Description | Selected |
|--------|-------------|----------|
| Publish to PyPI too | Both on PyPI, clean dependency chain | ✓ |
| Keep editable path | Co-develop locally | |
| Absorb into digitalmodel | Move shared infra in | |

### Licensing

| Option | Description | Selected |
|--------|-------------|----------|
| MIT (current) | Maximum adoption | ✓ |

### README Standards Showcase

| Option | Description | Selected |
|--------|-------------|----------|
| Showcase traceability | Lead with standards messaging | ✓ |

### PyPI Module Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Ship what's production | Only production-maturity modules | ✓ |

### Package Name

| Option | Description | Selected |
|--------|-------------|----------|
| Keep digitalmodel | Established, 305+ commits | ✓ |

### Parametric Studies (User-initiated)

**User's input:** "For analysis from digitalmodel, we will populate and maintain all the parametric studies and present as rich charts as lookup for clients in aceengineer website."

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, Tier 1 | Core to website value prop | ✓ |
| Tier 2 | After Tier 1 modules | |
| Already exists informally | Formalize existing benchmarks | |

### Chart Rendering

| Option | Description | Selected |
|--------|-------------|----------|
| Python generates data, JS renders | JSON output, JS charts on website | ✓ |

---

## Updated Session (2026-03-27): Tech Debt Priorities

### Broken Structural Tests

| Option | Description | Selected |
|--------|-------------|----------|
| High priority | Fix before PyPI | ✓ |
| Fix only affected modules | Active modules only | |
| Defer entirely | New modules self-contained | |

### Test Fix Target

| Option | Description | Selected |
|--------|-------------|----------|
| All 150 | Fix every broken test | ✓ |

### 455 Standards Gaps

| Option | Description | Selected |
|--------|-------------|----------|
| Prioritized subset | Pick 20-50 valuable gaps | ✓ |

### Coverage Metrics

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, refresh | Run coverage, update coverage.json | ✓ |

### Architecture Debt

| Option | Description | Selected |
|--------|-------------|----------|
| Import path cleanup | Fix broken imports causing failures | ✓ |

### PyPI Readiness Milestone

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, dedicated milestone | Explicit PyPI readiness milestone | ✓ |

### CI Pipeline

| Option | Description | Selected |
|--------|-------------|----------|
| Add CI to roadmap | GitHub Actions tests + coverage | ✓ |

### Coverage Threshold

| Option | Description | Selected |
|--------|-------------|----------|
| Keep 80% | Already configured in pyproject.toml | ✓ |

### CHANGELOG

| Option | Description | Selected |
|--------|-------------|----------|
| Formalize for PyPI | Keep a Changelog format | ✓ |

---

## Updated Session (2026-03-27): OrcaFlex Scope

### Scope Definition

| Option | Description | Selected |
|--------|-------------|----------|
| Automate model generation | YAML config -> .dat file generation | ✓ |

### Model Types

| Option | Description | Selected |
|--------|-------------|----------|
| Subsea pipelines/risers | Most common in client work | ✓ |

### Module Architecture

| Option | Description | Selected |
|--------|-------------|----------|
| Standalone module | Own module in orcaflex/ | ✓ |

### OrcaWave

| Option | Description | Selected |
|--------|-------------|----------|
| Include OrcaWave | Bundle as Orca suite, RAOs feed into OrcaFlex | ✓ |

### Config Format

| Option | Description | Selected |
|--------|-------------|----------|
| YAML configs | ASCII-first consistency | ✓ |

### Execution Model

| Option | Description | Selected |
|--------|-------------|----------|
| Generate locally, run remotely | .dat on any machine, OrcaFlex on Windows | ✓ |

### Result Extraction

| Option | Description | Selected |
|--------|-------------|----------|
| Generation only (for now) | Post-processing future milestone | ✓ |

### Configuration Count

| Option | Description | Selected |
|--------|-------------|----------|
| 1-2 canonical configs | Static catenary riser + simple pipeline | ✓ |

---

## Updated Session (2026-03-27): Roadmap Structure

### Format

| Option | Description | Selected |
|--------|-------------|----------|
| Milestone-based | Named milestones with phases | ✓ |

### Milestone Count

| Option | Description | Selected |
|--------|-------------|----------|
| 2-3 milestones | Near-term, actionable | ✓ |

### File Location

| Option | Description | Selected |
|--------|-------------|----------|
| Root ROADMAP.md | Repo root, same as workspace-hub | ✓ |

### Phase Format

| Option | Description | Selected |
|--------|-------------|----------|
| GSD-compatible | Numbered phases, /gsd commands | ✓ |

### M1 Focus

| Option | Description | Selected |
|--------|-------------|----------|
| PyPI readiness | Tests, imports, CI, publish | ✓ |

### Cross-references

| Option | Description | Selected |
|--------|-------------|----------|
| Self-contained | No workspace-hub references | ✓ |

### Parametric Studies Milestone

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated milestone | Own infrastructure milestone | ✓ |

### Milestone Ordering

| Option | Description | Selected |
|--------|-------------|----------|
| M1=PyPI, M2=Tier 1+parametric, M3=next | Foundation then modules then expand | ✓ |

### Module Registry Refresh

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, refresh maturity | Audit vs registered level | ✓ |

### README

| Option | Description | Selected |
|--------|-------------|----------|
| Trim to essentials | Short, professional, PyPI-friendly | ✓ |

---

## Claude's Discretion

- Non-Python consumer architecture (API layer feasibility)
- Exact milestone phase counts and ordering
- Specific standards gaps for prioritized subset
- Module-registry.yaml schema updates

## Deferred Ideas

- OrcaFlex result extraction/post-processing — future milestone
- Remote execution automation (SSH to licensed machine)
- Sphinx/MkDocs API documentation
- Module boundary review (digitalmodel vs assetutilities)
