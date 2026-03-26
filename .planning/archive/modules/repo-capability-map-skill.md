# Plan: `repo-capability-map` Skill

> **Module:** workspace-hub/skills
> **Status:** Draft
> **Date:** 2026-01-29

## Summary

Create a skill that analyzes repository modules for current capabilities, groups them by domain, and identifies strategic gaps against mission objectives. This is complementary to the existing `repository-health-analyzer` (which asks "is the repo well-maintained?") -- this skill asks "what can this repo do, and what's missing?"

## Files to Create

| # | File | Purpose |
|---|------|---------|
| 1 | `.claude/skills/coordination/workspace/repo-capability-map/SKILL.md` | Main skill definition: taxonomy, maturity model, methodology, output format |
| 2 | `.claude/skills/coordination/workspace/repo-capability-map/actions/scan.md` | Step-by-step agent instructions for scanning a repo |
| 3 | `.claude/skills/coordination/workspace/repo-capability-map/actions/report.md` | Instructions for generating console summary + markdown report |
| 4 | `.claude/skills/coordination/workspace/repo-capability-map/actions/gaps.md` | Gap analysis procedure against mission objectives |
| 5 | `.claude/skills/coordination/workspace/repo-capability-map/actions/compare.md` | Side-by-side capability comparison between two repos |
| 6 | `.claude/skills/coordination/workspace/repo-capability-map/templates/repo-profile.md` | Template for per-repo capability profile |
| 7 | `.claude/skills/coordination/workspace/repo-capability-map/templates/capability-report.md` | Template for full workspace capability report |
| 8 | `.claude/commands/workspace-hub/repo-capability-map.md` | Command entry point (routes to SKILL.md) |
| 9 | `.claude/skill-registry.yaml` | Add new entry for the command |

## Command Interface

```
/repo-capability-map [subcommand] [options]
```

| Subcommand | Description |
|------------|-------------|
| `scan` (default) | Full scan of all active repos |
| `scan <repo>` | Scan a single repo |
| `domain <name>` | Show capabilities for one domain (ENG, DATA, WEB, BIZ, INFRA, KNOW, FIN) |
| `gaps` | Show only gap analysis vs mission objectives |
| `report` | Generate full markdown report to `reports/capability-map/` |
| `compare <r1> <r2>` | Side-by-side capability comparison between two repos |

Options: `--format`, `--output`, `--include-dormant`, `--maturity-filter`

## Analysis Methodology

For each repo, the agent reads files in priority order:

**Tier 1 - Declared Identity** (highest confidence)
- `README.md` -- mission, capabilities snapshot, features
- `CLAUDE.md` -- tech stack, project rules, domain keywords
- `.agent-os/product/mission.md` -- strategic phases, success metrics
- `.agent-os/product/roadmap.md` -- planned features, completion status

**Tier 2 - Structural Evidence**
- `src/` directory tree -- module names, sub-packages
- `.claude/skills/` -- domain skills (each skill = capability signal)
- `pyproject.toml` / `package.json` -- dependencies, entry points
- `tests/` and `docs/` structure

**Tier 3 - Behavioral Evidence**
- `git log --oneline -30` -- recent activity, development focus
- `scripts/` directory -- automation capabilities
- `data/` / `config/` contents -- data domains

## Capability Taxonomy

Two-level hierarchy: **Domain** > **Capability Area**

| Domain ID | Domain Name | Example Repos |
|-----------|-------------|---------------|
| `ENG` | Engineering Analysis | digitalmodel, seanation, frontierdeepwater |
| `DATA` | Data & Analytics | worldenergydata, energy |
| `WEB` | Web & Frontend | aceengineer-website |
| `BIZ` | Business Operations | aceengineer-admin |
| `INFRA` | Infrastructure & DevOps | pyproject-starter, assetutilities |
| `KNOW` | Knowledge & Documentation | achantas-media, teamresumes |
| `FIN` | Financial & Investments | investments, assethold |

Taxonomy is **discovered dynamically** -- the agent maps findings to known domains but can create new ones.

## Maturity Model

| Level | Label | Criteria |
|-------|-------|----------|
| 1 | **Nascent** | Mentioned in mission/roadmap but no implementation |
| 2 | **Emerging** | Partial implementation, <50% test coverage, active WIP |
| 3 | **Established** | Working implementation with tests, docs, CLI/API available |
| 4 | **Mature** | Production-grade, 80%+ coverage, skills defined, decision history |

Assessment based on observable artifacts (files exist, tests present, skills defined) -- not subjective judgments.

## Output Format

### Console Summary

```
WORKSPACE CAPABILITY MAP | 2026-01-29 | Repos: 25

DOMAIN: Engineering Analysis (ENG)
  Repos: digitalmodel, seanation, doris, saipem
  | Capability Area        | Maturity    | Lead Repo     |
  | OrcaFlex Modeling      | Mature      | digitalmodel  |
  | Mooring Design         | Mature      | digitalmodel  |
  | Fatigue Analysis       | Established | digitalmodel  |

GAP ANALYSIS vs MISSION
  COVERED:  [x] Engineering assets (digitalmodel)
  GAPS:     [ ] Wind energy economics (not started)
```

### Markdown Report

Saved to `reports/capability-map/capability-report-YYYY-MM-DD.md` with sections:
- Executive Summary (counts, maturity distribution)
- Domain breakdowns (capability matrix per domain)
- Cross-domain dependencies
- Gap analysis (covered objectives + uncovered)
- Recommendations

## Integration Points

- `repository-health-analyzer` -- health gates capability scanning
- `work-queue` -- gap analysis can feed `/work add` items
- `claude-reflect` -- periodic reflection includes capability changes
- `compliance-check` -- repos missing CLAUDE.md get lower maturity

## Implementation Sequence

1. Create `SKILL.md` (core definition with taxonomy + maturity model)
2. Create `actions/scan.md` (extraction logic)
3. Create `actions/gaps.md` (gap analysis procedure)
4. Create `actions/report.md` (output generation)
5. Create `actions/compare.md` (side-by-side repo comparison)
6. Create `templates/` (repo-profile.md, capability-report.md)
7. Create `repo-capability-map.md` command file
8. Update `skill-registry.yaml`

## Verification

1. Run `/repo-capability-map scan digitalmodel` -- verify single-repo scan produces a sensible capability profile
2. Run `/repo-capability-map` -- verify full workspace scan groups repos by domain
3. Run `/repo-capability-map gaps` -- verify gap analysis references mission objectives
4. Run `/repo-capability-map report` -- verify markdown report generated at expected path
5. Run `/repo-capability-map compare digitalmodel worldenergydata` -- verify side-by-side comparison
6. Confirm the command appears in `/skills` list after registry update
