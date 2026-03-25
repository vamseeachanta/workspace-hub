# Workspace Hub

## Overview

Engineering workspace orchestrating a portfolio of Python packages, data repositories, and web properties for offshore/subsea engineering. The hub coordinates 24 git submodules through shared tooling, AI agent configuration, and cross-repo automation.

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
- **Git:** 24 submodules, commit to main + push; branch only for multi-session work

## Engineering Domains

- Offshore/subsea structural analysis (cathodic protection, VIV, fitness-for-service)
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

## Owner

Vamsee — solo engineer, repo owner, all agent sessions.
