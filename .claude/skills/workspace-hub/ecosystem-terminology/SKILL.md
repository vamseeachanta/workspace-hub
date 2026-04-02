---
name: ecosystem-terminology
version: 1.0.0
category: workspace-hub
applies-to:
- claude
- codex
- gemini
invocation: /ecosystem-terminology
description: 'Canonical names, abbreviations, and relationship vocabulary for the
  workspace-hub ecosystem. Load this when naming repos, modules, machines, files,
  or expanding acronyms to ensure consistency across humans and agents. type: reference

  '
triggers:
- ecosystem terminology
- canonical name
- repo name
- what is WRK
- abbreviation
- what does it mean
- naming convention
related_skills:
- repo-structure
tags:
- naming
- conventions
- repos
- acronyms
- reference
type: reference
---

# Ecosystem Terminology

> Single authoritative reference for names, abbreviations, and relationships.
> Correct these first before writing any code, commit, or document.

## 1 — Canonical Repo Names

> This section covers **core / tier-1 repos** and commonly referenced submodules.
> The full submodule list is in `.gitmodules` (24 submodules total as of 2026-03).
> Repos not listed below follow the same pattern: use the exact name in `.gitmodules`.

### Core / Tier-1 Repos (Python, full test suite)

| Repo | Canonical ID | Package Name | Tier | Maturity | Aliases (acceptable) | Do-Not-Use |
|------|-------------|-------------|------|----------|----------------------|-----------|
| workspace-hub | `workspace-hub` | — | hub | stable | hub | workspace_hub, WorkspaceHub, wshub |
| assetutilities | `assetutilities` | `assetutilities` | tier-1 | stable | au | asset_utilities, asset-utilities, AssetUtilities, asset_util |
| digitalmodel | `digitalmodel` | `digitalmodel` | tier-1 | beta | dm | digital_model, digital-model, DigitalModel |
| worldenergydata | `worldenergydata` | `worldenergydata` | tier-1 | beta | wed | world_energy_data, WorldEnergyData, energydata |
| assethold | `assethold` | `assethold` | tier-1 | beta | ah | asset_hold, asset-hold, AssetHold |
| OGManufacturing | `OGManufacturing` | `ogmanufacturing` | tier-1 | alpha | ogm | og_manufacturing, og-manufacturing, ogmanufacturing (as repo ID) |

> **Import note**: `OGManufacturing` is the git submodule name (PascalCase); its Python
> package is `ogmanufacturing` (lowercase). Never swap them.

### Other Submodules (non-Python or special-purpose)

| Repo | Canonical ID | Category | Do-Not-Use |
|------|-------------|---------|-----------|
| aceengineer-website | `aceengineer-website` | site | aceengineer_website, ace-website |
| aceengineer-admin | `aceengineer-admin` | admin | aceengineer_admin |
| achantas-data | `achantas-data` | data | achantas_data |
| achantas-media | `achantas-media` | media | achantas_media |
| acma-projects | `acma-projects` | projects | acma_projects |
| client_projects | `client_projects` | client | client-projects, clientprojects |
| CAD-DEVELOPMENTS | `CAD-DEVELOPMENTS` | cad | cad-developments, cad_developments |
| doris | `doris` | tools | — |
| frontierdeepwater | `frontierdeepwater` | data | frontier_deepwater, FrontierDeepwater |
| hobbies | `hobbies` | personal | — |
| investments | `investments` | finance | — |
| pdf/large-reader | `pdf/large-reader` | tools | pdf_large_reader |
| pyproject-starter | `pyproject-starter` | template | pyproject_starter |
| rock-oil-field | `rock-oil-field` | data | rock_oil_field |
| sabithaandkrishnaestates | `sabithaandkrishnaestates` | personal | sabithaandkrishna-estates |
| saipem | `saipem` | client | — |
| sd-work | `sd-work` | work | sd_work |
| seanation | `seanation` | data | — |
| teamresumes | `teamresumes` | hr | team_resumes, team-resumes |

## 2 — Relationship Vocabulary

| Term | Definition |
|------|-----------|
| **hub** | `workspace-hub` — the orchestration repo; contains skills, work-queue, scripts, config |
| **submodule** | Any repo registered in `.gitmodules` under `workspace-hub` (24 total as of 2026-03); includes tier-1, site, data, personal repos |
| **tier-1 repo** | A submodule with a `pyproject.toml`, `uv.lock`, and full test suite; currently: assetutilities, digitalmodel, worldenergydata, assethold, OGManufacturing |
| **adapter file** | `CLAUDE.md`, `CODEX.md`, `GEMINI.md` — thin per-agent configuration files (≤20 lines); never put logic here, use skills instead |
| **harness** | The tooling layer inside hub: skills, work-queue, scripts, config, rules |
| **WRK** | A work item tracked in `.claude/work-queue/` with a `WRK-NNN` identifier |
| **stage** | One numbered step in the 20-stage WRK lifecycle (1=Capture … 20=Archive) |
| **phase** | A grouping of related stages (e.g., "planning phase" = stages 2-7) |
| **checkpoint** | `checkpoint.yaml` snapshot written after each stage to enable safe resume |
| **gate** | A hard stop requiring human confirmation or verifiable script output before proceeding |
| **cross-review** | Multi-provider AI review (Claude + Codex + Gemini) — Codex is a hard gate |
| **AC** | Acceptance Criteria — the testable conditions that define WRK completion |
| **evidence** | Files in `assets/WRK-NNN/evidence/` that record gate passage |
| **skill** | A `SKILL.md` file loaded on demand to guide agent behaviour for a specific task type |
| **orchestrator** | The AI agent that owns the session; delegates to subagents |
| **subagent** | Agent spawned by the orchestrator to isolate context or run parallel work |

## 3 — File / Directory Naming

| Context | Correct | Incorrect |
|---------|---------|-----------|
| Work-queue directory | `work-queue` | `work_queue`, `workqueue` |
| Skill definition file | `SKILL.md` | `skill.md`, `Skill.md`, `SKILL.yaml` |
| WRK asset dir | `assets/WRK-1098/` | `assets/wrk-1098/`, `assets/WRK1098/` |
| Evidence dir | `evidence/` | `evidences/`, `gate-evidence/` |
| Script files | `kebab-case.sh` | `snake_case.sh`, `camelCase.sh` |
| Python source | `snake_case.py` | `kebab-case.py`, `camelCase.py` |
| Stage exit artifact | `stage-evidence.yaml` | `stage_evidence.yaml`, `stageEvidence.yaml` |
| GitHub issue (review surface) | GitHub issue URL | `WRK-NNN-lifecycle.html` (deprecated) |
| Config files | `kebab-case.yaml` | `snake_case.yaml` |
| Commands dir | `.claude/commands/` | `.claude/command/`, `.claude/cmds/` |

## 4 — Acronyms & Abbreviations

| Acronym | Expansion | Domain |
|---------|-----------|--------|
| WRK | Work item (tracked queue entry) | harness |
| AC | Acceptance Criteria | harness |
| TDD | Test-Driven Development | engineering |
| GTM | Go-To-Market | strategy |
| CP | Cathodic Protection | engineering |
| VIV | Vortex-Induced Vibration | engineering |
| FFS | Fitness-For-Service | engineering |
| EIA | Energy Information Administration | data |
| BSEE | Bureau of Safety and Environmental Enforcement | data |
| OG | Oil and Gas | domain |
| HPC | High-Performance Computing | infra |
| CFD | Computational Fluid Dynamics | infra |
| FEA | Finite Element Analysis | infra |
| PEP | Python Enhancement Proposal | python |
| SRP | Single Responsibility Principle | patterns |
| DI | Dependency Injection | patterns |
| CI | Continuous Integration | devops |
| CD | Continuous Deployment | devops |
| RI | Resource Intelligence (Stage 2 artefact) | harness |
| HTML | (deprecated) formerly Lifecycle review document; now GitHub issue is the review surface | harness |
| MCP | Model Context Protocol (Claude tool server standard) | ai |
| QA | Quality Assurance | engineering |
| CLI | Command-Line Interface | tools |
| YAML | YAML Ain't Markup Language (config file format) | infra |
| UV | Astral `uv` — the Python package/project manager used throughout this workspace | python |

## 5 — Machines / People

| Canonical | Aliases (OK in casual chat) | Never Use | Notes |
|-----------|---------------------------|-----------|-------|
| `dev-primary` | primary, ace1-machine | ace1, linux-1, machine1 | Primary orchestration machine |
| `dev-secondary` | secondary, ace2-machine | ace2, linux-2, machine2 | Secondary Linux / CFD-FEA dev |
| `licensed-win-1` | ansys-machine, orcaflex-machine | ansys5, acma5 | Windows, OrcaFlex license-locked |
| `licensed-win-2` | windows-machine | ws14, acma14 | Windows 11 workstation |
| `gali-linux-compute-1` | gali-compute | gali1, compute1 | Heavy-compute Linux (planned) |
| vamsee | — | user (in evidence `reviewer` field use `vamsee`) | Repo owner |

## 6 — Do-Not-Use List

| Deprecated / Wrong Name | Use Instead | Reason |
|------------------------|-------------|--------|
| `asset_utilities` | `assetutilities` | Underscore variant — breaks imports |
| `digital_model` | `digitalmodel` | Underscore variant — breaks imports |
| `world_energy_data` | `worldenergydata` | Underscore variant — breaks imports |
| `asset_hold` | `assethold` | Underscore variant |
| `og_manufacturing` | `OGManufacturing` (repo) / `ogmanufacturing` (package) | Mixed-case rule |
| `work_queue` | `work-queue` | Wrong directory name |
| `skill.md` | `SKILL.md` | Incorrect capitalisation |
| `ace1`, `linux-1` | `dev-primary` | Non-canonical machine shorthand |
| `ace2`, `linux-2` | `dev-secondary` | Non-canonical machine shorthand |
| `AssetUtilities` | `assetutilities` | PascalCase is wrong for package/repo ID |
| `DigitalModel` | `digitalmodel` | PascalCase is wrong for package/repo ID |
| `WorldEnergyData` | `worldenergydata` | PascalCase is wrong for package/repo ID |
| `WRK_NNN` | `WRK-NNN` | Hyphen required in WRK identifiers |
| `wrk-nnn` | `WRK-NNN` | Must be uppercase |
| `stage_evidence` | `stage-evidence` | Hyphen-case for all YAML artefact names |
| `user` (reviewer field) | `vamsee` | Human allowlist uses the name, not role |

## Iron Law

> No repo, package, machine, file, or identifier shall be referenced by a non-canonical name — check this skill's tables before writing any name.

## Rationalization Defense

| Excuse | Reality |
|--------|---------|
| "The user typed it this way, I'm just matching their input" | You are the enforcement layer. Correct non-canonical names silently — do not propagate errors. |
| "It's just a comment / commit message, not code" | Non-canonical names in prose train future agents (and humans) to use the wrong name. Every occurrence matters. |
| "I know the right name, this is close enough" | `asset_utilities` breaks imports. `digital-model` breaks directory lookups. Close enough is broken. |
| "There's no entry in the table for this" | If it is not in the table, check `.gitmodules` for the exact spelling. Never guess. |

## Red Flags

These phrases signal you are about to violate the Iron Law:
- "I think the repo is called..."
- "the package name is probably..."
- using underscores in a repo name without checking
- using PascalCase for a package import
- referencing a machine as "ace1" or "linux-1"
