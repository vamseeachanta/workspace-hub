# Workspace Hub — Capabilities Summary

> **Central engineering workspace managing 20+ tier-1 and tier-2 repositories**
>
> **Version:** 2.0.0
> **Last Updated:** 2026-04-02
> **Status:** ✅ Production

---

## Architecture

Workspace-hub follows the **Control-Plane Contract** (`docs/standards/CONTROL_PLANE_CONTRACT.md`):

- **`AGENTS.md`** is the canonical entry point for every repository
- **Provider adapters** (`.claude/`, `.codex/`, `.gemini/`) extend but never contradict `AGENTS.md`
- **GSD workflow** is the standard task execution framework (replaces legacy SPARC/Claude Flow)
- **GitHub Issues** are the single source of truth for task tracking — no local work queues

### Provider Model

| Provider | Adapter Path | Role |
|----------|-------------|------|
| Claude Code | `.claude/` | Primary orchestrator, implementation, skills |
| OpenAI Codex | `.codex/` | Code review (per AI Review Routing Policy) |
| Google Gemini | `.gemini/` | Triggered review on specific criteria |

See: `docs/standards/AI_REVIEW_ROUTING_POLICY.md`

---

## Skills System

**Total skills:** 2,734 (568 active, 2,166 archived)

### Active Skill Categories

| Category | Count | Description |
|----------|-------|-------------|
| `_internal` | 128 | Framework internals and runtime skills |
| `engineering` | 87 | Engineering domain (OrcaFlex, FreeCAD, solvers) |
| `data` | 77 | Data processing and analysis |
| `business` | 70 | Business operations and strategy |
| `_core` | 53 | Core framework capabilities |
| `development` | 52 | Software development patterns |
| `gsd-*` | 57 | GSD workflow commands (gsd-do, gsd-next, etc.) |
| `operations` | 15 | DevOps and operational tasks |
| `workspace-hub` | 12 | Workspace management |
| `ai` | 9 | AI/ML specific skills |
| `science` | 6 | Scientific computing |
| `digitalmodel` | 2 | DigitalModel-specific skills |

### Skill Locations

```
.claude/skills/
├── _archive/          # 2,166 retired skills
├── _core/             # Framework essentials
├── _internal/         # Runtime internals
├── ai/                # AI/ML skills
├── business/          # Business domain
├── data/              # Data processing
├── development/       # Software dev patterns
├── digitalmodel/      # DigitalModel-specific
├── engineering/       # Engineering solvers
├── gsd-*/             # 57 GSD workflow commands
├── operations/        # DevOps/ops
├── science/           # Scientific computing
└── workspace-hub/     # Workspace management
```

Usage: Skills are loaded automatically by Claude Code when task patterns match skill triggers.

---

## Quality & Automation Scripts

### Scripts (`scripts/`)

| Script | Purpose |
|--------|---------|
| `scripts/quality/doc-staleness-scanner.py` | Scan docs for freshness (current/stale/critical) |
| `scripts/quality/check_doc_drift.py` | Detect documentation vs. code drift |
| `scripts/quality/check_config_drift.py` | Configuration drift detection |
| `scripts/quality/check_complexity_ratchet.py` | Complexity ratchet enforcement |
| `scripts/quality/api-audit.py` | API surface audit |
| `scripts/quality/quality_gap_report.py` | Quality gap analysis |
| `scripts/quality/dep-health.sh` | Dependency health check |
| `scripts/quality/check-all.sh` | Run all quality checks |

### Cron Automation

Scheduled tasks defined in `config/schedule-tasks.yaml` (single source of truth).
Generated via `scripts/operations/setup-cron.sh --replace`.

Key scheduled tasks:
- Nightly GSD researcher
- Cron health checks
- Repository sync
- Quality checks

---

## Repository Ecosystem

### Tier-1 Repositories (Core Engineering)

| Repository | Domain |
|-----------|--------|
| `digitalmodel` | Engineering simulation (OrcaFlex, OrcaWave, FreeCAD) |
| `assetutilities` | Shared Python utilities |
| `assethold` | Asset management |
| `worldenergydata` | Energy industry data |

### Tier-2 Repositories (Business & Projects)

See: `docs/modules/tiers/TIER2_REPOSITORY_INDEX.md` for full list.

### Key Directories

```
workspace-hub/
├── .claude/              # Claude Code config, skills, state
│   ├── skills/           # 2,734 skills (568 active)
│   ├── state/            # Runtime state and reports
│   └── rules/            # Claude behavioral rules
├── config/               # Central configuration
│   └── schedule-tasks.yaml  # Cron task definitions
├── docs/                 # Documentation tree
│   ├── standards/        # Engineering standards
│   ├── research/         # Technical evaluations
│   ├── plans/            # Implementation plans
│   └── reports/          # Generated reports
├── scripts/              # Automation scripts
│   ├── quality/          # Quality checks
│   └── operations/       # Operational scripts
├── tests/                # Test suites
├── templates/            # Project templates
└── [tier-1 repos]/       # Cloned tier-1 repositories
```

---

## Development Workflow

1. **Plan before acting** — explicit plan + user approval before implementation
2. **TDD mandatory** — tests before implementation; no exceptions
3. **`uv run`** — always use `uv run` for Python, never bare `python3`
4. **Git:** commit to `main` + push immediately; branch only for multi-session work
5. **Reviews:** verdicts APPROVE|MINOR|MAJOR; resolve MAJOR before completion

### Review Routing

- Claude orchestrates and implements
- Codex reviews (default reviewer)
- Gemini reviews on specific triggers

See: `docs/standards/AI_REVIEW_ROUTING_POLICY.md`

---

## Knowledge & Intelligence Ecosystem

The workspace-hub hosts a large-scale intelligence layer alongside its code and automation:

- **LLM-Wikis:** 19,300+ pages across 5 domains (engineering, marine-engineering, maritime-law, naval-architecture, personal) under `knowledge/wikis/`
- **Document-intelligence pipeline:** 1M+ indexed documents, 639K summaries, 425 tracked standards in `data/document-index/`
- **Design code registry:** ~30 engineering codes (DNV, API, ISO, ASTM, BS) in `data/design-codes/code-registry.yaml`
- **Knowledge seeds:** Domain seed files in `knowledge/seeds/` for wiki bootstrapping

Architecture and navigation: [docs/document-intelligence/](document-intelligence/README.md)

## Version History

### v2.0.0 (2026-04-02)
- Complete rewrite removing stale patterns (Claude Flow, SPARC, .agent-os, droid)
- Updated to reflect Control-Plane Contract architecture
- Updated skill counts (2,734 total, 568 active)
- Aligned with GSD workflow and provider adapter model
- Removed references to deprecated tools and patterns

### v1.0.0 (2025-10-05)
- Initial comprehensive summary (historical — largely superseded)
