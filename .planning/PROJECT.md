# Workspace Hub

## Overview

Engineering workspace orchestrating a portfolio of Python packages, data repositories, and web properties for offshore/subsea engineering. The hub coordinates 24 independent git repositories through shared tooling, AI agent configuration, and cross-repo automation.

**Theme:** Tethering timeless engineering to a single source of truth — every calculation traces to its standard, every standard to its implementation.

## Architecture

- **Hub repo** (`workspace-hub`) — orchestration layer: agent config, skills, scripts, CI coordination
- **Tier-1 Python packages** — `assetutilities`, `digitalmodel`, `worldenergydata`, `assethold`, `OGManufacturing` — each with `pyproject.toml`, `uv.lock`, full test suites
- **Web properties** — `aceengineer-website` (public site)
- **Corporate** — `aceengineer-admin` (corporate administration)
- **Data repos** — `frontierdeepwater`, `rock-oil-field`, `seanation`, `worldenergydata`
- **Personal** — `achantas-data`, `achantas-media`
- **Specialty** — `CAD-DEVELOPMENTS`, `doris`, `client_projects`

## Tech Stack

- **Languages:** Python (primary), Bash (scripts), JavaScript (hooks/GSD)
- **Package management:** `uv` exclusively — never bare `python3`
- **AI agents:** Claude Code, Codex CLI, Gemini CLI — multi-provider with cross-review
- **Workflow:** GSD framework (discuss → plan → execute → verify → ship)
- **Task tracking:** GitHub Issues (no local work queue)
- **Git:** 24 independent repos (submodules removed 2026-03-25), commit to main + push; branch only for multi-session work

## Engineering Domains

- Offshore/subsea structural analysis (cathodic protection, VIV, fitness-for-service, on-bottom stability, wall thickness, fatigue)
- Computational fluid dynamics (OpenFOAM) and finite element analysis
- Energy data aggregation (EIA, BSEE, global production)
- Marine/maritime legal and regulatory compliance
- GIS and digital twin modeling

## Machines

| Name | Role |
|------|------|
| `dev-primary` | Primary orchestration, development |
| `dev-secondary` | Secondary Linux, CFD/FEA workloads |
| `licensed-win-1` | Windows, OrcaFlex/ANSYS license-locked |
| `licensed-win-2` | Windows 11 workstation |

## Constraints

- TDD mandatory — tests before implementation
- Plan before acting — explicit plan + user approval
- Secrets via environment variables only
- CLAUDE.md/AGENTS.md ≤ 20 lines — excess goes to skills/docs
- Reviews: APPROVE/MINOR/MAJOR verdicts; resolve MAJOR before completion

## Current State (v1.0 shipped 2026-03-30)

Shipped v1.0 Foundation Sprint across 6 phases (21 plans) in 5 days.

**What shipped:**
- 3 new digitalmodel calculation modules (OBS, wall thickness, spectral fatigue) at 90.5% test coverage
- EIA/BSEE/SODIR data pipelines with Parquet output, staleness monitoring, email alerting
- aceengineer.com: interactive calculators, pricing page, GA4 tracking, Schema.org SEO
- Enterprise funnel: case studies, calculator-to-case-study CTAs, contact form lead qualification, GitHub Issues prospect pipeline
- Nightly 4-domain research automation with model selection, validation, and 90-day pruning
- digitalmodel library-first vision, tiered development roadmap, trimmed README

**Validated requirements (v1.0):**
- ✓ 3+ new calculation modules with test coverage and standards traceability
- ✓ All active data sources updating with staleness monitoring
- ✓ Website with clear value prop, calculation demos, and contact flow
- ✓ Enterprise funnel with case studies, GA4 tracking, and prospect pipeline
- ✓ Nightly research automation running with quality controls
- ✓ digitalmodel vision and roadmap refreshed

## Current Milestone: v1.1 OrcaWave Automation

**Goal:** Automate the full OrcaWave vessel hull analysis workflow — from analysis type selection through to client-ready calculation reports — and prove it by generating reports for all existing examples.

**Target features:**
- Calculation report template refinement — redesign content flow for client experience: narrative structure, integrated RAO plots, hydro matrix presentation, QA summaries
- Analysis workflow automation — deterministic pipeline: identify analysis type → match closest example YAML → parametric update → execute on licensed machine → extract results → generate report
- Sensitivity analysis tooling — automated parameter sweeps to eliminate options before full analysis
- Batch report generation — run all existing examples (L00–L06, benchmarks) through the pipeline, produce standardized calculation reports
- OrcaFlex integration — results conversion to OrcaFlex vessel type format as part of the pipeline

## Key Decisions (v1.0)

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Library-first digitalmodel (not platform/SaaS) | Focus on calculation accuracy, not infrastructure | ✓ Good |
| OrcaFlex + CP as Tier 1 priorities | Highest client demand | ✓ Good |
| var for browser compat in JS engines | Match existing aceengineer codebase | ✓ Good |
| funnel_step event (not cta_click) for calculator→case study | Distinguish funnel progression from generic clicks | ✓ Good |
| 60h staleness threshold (not 36h) | Avoid Monday false positives with weekday-only schedule | ✓ Good |
| GitHub Issues for prospect pipeline | Private repo, no additional tooling needed | ✓ Good |
| Consultation-based pricing (no payment infra) | Lower complexity, higher-value engagements | — Pending |

## Owner

Vamsee — solo engineer, repo owner, all agent sessions.

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-29 after v1.1 milestone start*
