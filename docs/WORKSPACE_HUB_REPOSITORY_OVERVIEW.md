# Workspace-Hub Repository Overview

> Comprehensive guide to the workspace-hub ecosystem and its 25 managed repositories
>
> **Purpose**: This document helps humans and AI agents understand the workspace-hub structure, repository relationships, and navigation patterns.
>
> Version: 2.0.0
> Last Updated: 2026-03-31

---

## What is Workspace-Hub?

**Workspace-Hub** is a centralized repository management system that enables collaboration across 25 independent Git repositories through unified automation, synchronization, and orchestration tools.

### Key Characteristics

- **Multi-Repository Management**: Single control plane for 25 repositories
- **Repository Independence**: Each repo maintains its own history, access controls, and workflows
- **Unified Tooling**: Shared standards, scripts, and configurations
- **AI-Native Development**: GSD workflow with multi-provider AI agent support (Claude, Codex, Gemini)
- **Modular Architecture**: 8 specialized modules for different concerns

---

## Repository Architecture

```
workspace-hub/                    # Central management hub
├── AGENTS.md                     # Canonical workflow contract
├── .claude/                      # Claude provider adapter (skills, rules, docs)
├── .codex/                       # Codex provider adapter
├── .gemini/                      # Gemini provider adapter
├── docs/                         # Centralized documentation
├── modules/                      # Functional modules
├── scripts/                      # Automation scripts
├── config/                       # Shared configurations
├── templates/                    # Document templates
│
├── [25 managed repositories]/    # Individual project repositories
│   ├── Work repositories         # Professional/client projects
│   └── Personal repositories     # Personal projects
│
└── CLAUDE.md                     # Claude-specific configuration
```

---

## Repository Categories

Repositories are organized into **Work** (professional/client) and **Personal** categories.

### Work Repositories (Professional/Client Projects)

| Repository | Description | Domain |
|------------|-------------|--------|
| **digitalmodel** | Engineering Asset Lifecycle Management - Single source of truth for offshore, subsea, and marine engineering analysis | Marine/Offshore Engineering |
| **worldenergydata** | Comprehensive Python data library for energy industry (BSEE, production data, etc.) | Energy Data |
| **assetutilities** | Utilities for day-to-day business task automation | Utilities/Tools |
| **assethold** | Asset portfolio financial analysis (stocks, real estate) | Finance/Business |
| **frontierdeepwater** | Frontier Deepwater company documents and projects | Client Work |
| **doris** | Doris project work and documentation | Client Work |
| **saipem** | Saipem project work (umbilical installation analysis) | Client Work |
| **acma-projects** | ACMA Inc. high-level project data and action lists | Project Management |
| **seanation** | SeaNation project work | Client Work |
| **rock-oil-field** | Rock oil field analysis and documentation | Oil & Gas |
| **client_projects** | Client project management and documentation | Project Management |
| **teamresumes** | Team resume management | HR/Admin |
| **OGManufacturing** | Oil & Gas manufacturing documentation | Manufacturing |
| **CAD-DEVELOPMENTS** | CAD development work and documentation | Engineering/CAD |
| **heavyequipemnt-rag** | Heavy equipment RAG (retrieval-augmented generation) | AI/Engineering |
| **simpledigitalmarketing** | Digital marketing content and tools | Marketing |

### Personal Repositories

| Repository | Description | Domain |
|------------|-------------|--------|
| **aceengineer-admin** | ACE Engineer administrative tools | Personal/Admin |
| **aceengineer-strategy** | ACE Engineer business strategy | Personal/Strategy |
| **aceengineer-website** | ACE Engineer company website (www.aceengineer.com) | Website |
| **achantas-data** | Personal data management | Personal |
| **achantas-media** | Media and content management | Personal |
| **hobbies** | Personal hobbies and interests | Personal |
| **investments** | Investment tracking and analysis | Personal Finance |
| **sabithaandkrishnaestates** | Estate management | Personal |
| **sd-work** | Side work and projects | Personal |

---

## Repository Relationships

### Core Dependencies

```
workspace-hub (Central Hub)
    │
    ├── Standards & Configuration
    │   ├── AGENTS.md → Canonical workflow contract
    │   ├── .claude/, .codex/, .gemini/ → Provider adapters
    │   └── docs/modules/standards/ → Shared standards
    │
    ├── Utility Libraries
    │   └── assetutilities → Used by: digitalmodel, worldenergydata
    │
    ├── Engineering Analysis
    │   ├── digitalmodel → Core engineering analysis
    │   └── worldenergydata → Energy data library
    │
    └── Client Projects
        ├── frontierdeepwater
        ├── doris
        ├── saipem
        ├── seanation
        └── rock-oil-field
```

### Data Flow Relationships

```
worldenergydata (Data Source)
        │
        └──► digitalmodel (Engineering Models)
                 │
                 └──► Project-specific analyses
```

### Shared Utilities

```
assetutilities
    │
    ├──► digitalmodel (Engineering utilities)
    ├──► worldenergydata (Data utilities)
    └──► [Other repos as needed]
```

---

## Functional Modules

Workspace-hub contains 8 specialized modules:

| Module | Purpose | Location |
|--------|---------|----------|
| **git-management** | Git operations, synchronization | `modules/git-management/` |
| **automation** | Automation scripts, AI orchestration | `modules/automation/` |
| **ci-cd** | CI/CD pipelines, deployment | `modules/ci-cd/` |
| **monitoring** | Health checks, metrics | `modules/monitoring/` |
| **utilities** | Helper scripts, tools | `modules/utilities/` |
| **documentation** | Doc generation, templates | `modules/documentation/` |
| **config** | Shared configurations | `modules/config/` |
| **development** | Dev tools, hooks | `modules/development/` |

---

## AI Agent Integration

### GSD Workflow

All repositories use the GSD (Get Stuff Done) framework for AI-assisted development:
- **Plan before acting** — explicit plan + user approval before implementation
- **TDD mandatory** — tests before implementation
- **Multi-provider support** — Claude (.claude/), Codex (.codex/), Gemini (.gemini/)
- **Canonical entry point** — AGENTS.md defines the workflow contract per repo

### Control-Plane Contract

Each repo provides AI agents with context through:
- `AGENTS.md` — canonical workflow contract (what the repo does, how to work in it)
- `.claude/CLAUDE.md` — Claude-specific configuration and rules
- `.codex/` — Codex provider adapter
- `.gemini/` — Gemini provider adapter
- `.mcp.json` — MCP (Model Context Protocol) settings (where applicable)

---

## Development Workflow

### Standard Workflow Pattern

```
user_prompt.md → YAML config → Pseudocode → TDD → Implementation
        │              │            │          │
        │              │            │          └── Bash-based execution
        │              │            └── Gate-pass review
        │              └── AI generates from requirements
        └── Human-written requirements
```

### Key Standards

- **File Organization**: [FILE_ORGANIZATION_STANDARDS.md](modules/standards/FILE_ORGANIZATION_STANDARDS.md)
- **Testing**: [TESTING_FRAMEWORK_STANDARDS.md](modules/standards/TESTING_FRAMEWORK_STANDARDS.md)
- **Logging**: [LOGGING_STANDARDS.md](modules/standards/LOGGING_STANDARDS.md)
- **HTML Reports**: [HTML_REPORTING_STANDARDS.md](modules/standards/HTML_REPORTING_STANDARDS.md)

---

## Navigation Guide for AI Agents

### Quick Reference Paths

| Purpose | Path |
|---------|------|
| Workflow contract | `AGENTS.md` |
| Claude configuration | `CLAUDE.md` / `.claude/` |
| Documentation index | `docs/README.md` |
| Skills library | `.claude/skills/` |
| Rules | `.claude/rules/` |

### Understanding a Repository

When working with any repository:

1. **Read AGENTS.md** first (canonical workflow contract)
2. **Read CLAUDE.md** (Claude-specific configuration)
3. **Review README.md** for project overview
4. **Check docs/** for detailed documentation
5. **Review src/** for code structure
6. **Check tests/** for test patterns

### Cross-Repository Operations

```bash
# Sync all repositories
./scripts/repository_sync pull all

# Check status across all repos
./scripts/repository_sync status all

# Propagate standards
./scripts/compliance/propagate_claude_config.py
```

---

## Quick Commands

### Workspace Management

```bash
./scripts/workspace              # Interactive CLI menu
./scripts/repository_sync        # Repository sync tool
./scripts/compliance/verify_compliance.sh  # Check compliance
```

### Repository Operations

```bash
./scripts/repository_sync list all        # List all repos
./scripts/repository_sync pull work       # Pull work repos
./scripts/repository_sync sync personal   # Sync personal repos
```

---

## Repository Locations

All repositories are located as subdirectories of the workspace-hub root.

### Finding a Repository

```bash
# List all repositories (from workspace-hub root)
ls -d */

# Find repository by name
ls -d *model*/

# Check if repo exists
[ -d digitalmodel ] && echo "exists"
```

---

## Environment Management

### UV Package Manager

All Python repositories use UV for environment management:

```bash
# Create environment
uv venv

# Install dependencies
uv pip install -r requirements.txt

# Upgrade dependencies
uv pip upgrade
```

### Shared Configuration

- **TypeScript**: Centralized `tsconfig.json`
- **Testing**: Shared test configurations
- **MCP**: Claude Flow MCP integration
- **Git Hooks**: Standardized pre-commit hooks

---

## Getting Help

### Documentation Hierarchy

1. **This overview**: High-level understanding
2. **docs/README.md**: Documentation index
3. **Module-specific docs**: Detailed guidance per area
4. **Repository READMEs**: Project-specific information

### Key Documents

- [Workspace Hub Capabilities](WORKSPACE_HUB_CAPABILITIES_SUMMARY.md)
- [AI Agent Guidelines](modules/ai/AI_AGENT_GUIDELINES.md)
- [Development Workflow](modules/workflow/DEVELOPMENT_WORKFLOW.md)
- [CLI Documentation](modules/cli/WORKSPACE_CLI.md)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-23 | Initial comprehensive overview |
| 2.0.0 | 2026-03-31 | Reconciled inventory (25 repos), removed stale .agent-os/SPARC/Claude Flow refs, updated control-plane to AGENTS.md + provider adapters (#1531) |

---

*This document is part of the workspace-hub documentation infrastructure. For updates, see the docs/ directory.*
