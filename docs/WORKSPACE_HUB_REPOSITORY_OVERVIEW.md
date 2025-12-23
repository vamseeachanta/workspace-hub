# Workspace-Hub Repository Overview

> Comprehensive guide to the workspace-hub ecosystem and its 26+ managed repositories
>
> **Purpose**: This document helps humans and AI agents understand the workspace-hub structure, repository relationships, and navigation patterns.
>
> Version: 1.0.0
> Last Updated: 2025-12-23

---

## What is Workspace-Hub?

**Workspace-Hub** is a centralized repository management system that enables collaboration across 26+ independent Git repositories through unified automation, synchronization, and orchestration tools.

### Key Characteristics

- **Multi-Repository Management**: Single control plane for 26+ repositories
- **Repository Independence**: Each repo maintains its own history, access controls, and workflows
- **Unified Tooling**: Shared standards, scripts, and configurations
- **AI-Native Development**: SPARC methodology with Claude Flow orchestration
- **Modular Architecture**: 8 specialized modules for different concerns

---

## Repository Architecture

```
workspace-hub/                    # Central management hub
├── .agent-os/                    # Agent OS configuration
│   └── product/                  # Mission, tech-stack, roadmap
├── docs/                         # Centralized documentation
├── modules/                      # Functional modules
├── scripts/                      # Automation scripts
├── config/                       # Shared configurations
├── templates/                    # Document templates
│
├── [26+ managed repositories]/   # Individual project repositories
│   ├── Work repositories         # Professional/client projects
│   └── Personal repositories     # Personal projects
│
└── CLAUDE.md                     # AI agent configuration
```

---

## Repository Categories

Repositories are organized into **Work** (professional/client) and **Personal** categories.

### Work Repositories (Professional/Client Projects)

| Repository | Description | Domain |
|------------|-------------|--------|
| **digitalmodel** | Engineering Asset Lifecycle Management - Single source of truth for offshore, subsea, and marine engineering analysis | Marine/Offshore Engineering |
| **energy** | Energy sector analysis and data processing | Energy Industry |
| **worldenergydata** | Comprehensive Python data library for energy industry (BSEE, production data, etc.) | Energy Data |
| **assetutilities** | Utilities for day-to-day business task automation | Utilities/Tools |
| **frontierdeepwater** | Frontier Deepwater company documents and projects | Client Work |
| **doris** | Doris project work and documentation | Client Work |
| **saipem** | Saipem project work (umbilical installation analysis) | Client Work |
| **acma-projects** | ACMA Inc. high-level project data and action lists | Project Management |
| **seanation** | SeaNation project work | Client Work |
| **rock-oil-field** | Rock oil field analysis and documentation | Oil & Gas |
| **ai-native-traditional-eng** | AI-native approaches for traditional engineering workflows | AI/Engineering |
| **client_projects** | Client project management and documentation | Project Management |
| **teamresumes** | Team resume management | HR/Admin |
| **pyproject-starter** | Python project starter template | Development Tools |
| **assethold** | Asset holding and management | Business |
| **OGManufacturing** | Oil & Gas manufacturing documentation | Manufacturing |

### Personal Repositories

| Repository | Description | Domain |
|------------|-------------|--------|
| **aceengineer-admin** | ACE Engineer administrative tools | Personal/Admin |
| **aceengineer-website** | ACE Engineer company website (www.aceengineer.com) | Website |
| **aceengineercode** | ACE Engineer code repositories | Development |
| **achantas-data** | Personal data management | Personal |
| **achantas-media** | Media and content management | Personal |
| **hobbies** | Personal hobbies and interests | Personal |
| **investments** | Investment tracking and analysis | Personal Finance |
| **sabithaandkrishnaestates** | Estate management | Personal |
| **sd-work** | Side work and projects | Personal |

### Mixed (Work + Personal)

| Repository | Description |
|------------|-------------|
| **aceengineer-website** | Also serves professional purposes |

---

## Repository Relationships

### Core Dependencies

```
workspace-hub (Central Hub)
    │
    ├── Standards & Configuration
    │   ├── CLAUDE.md → Propagated to all repos
    │   ├── .agent-os/ → Shared Agent OS config
    │   └── docs/modules/standards/ → Shared standards
    │
    ├── Utility Libraries
    │   ├── assetutilities → Used by: digitalmodel, energy, worldenergydata
    │   └── pyproject-starter → Template for new projects
    │
    ├── Engineering Analysis
    │   ├── digitalmodel → Core engineering analysis
    │   ├── energy → Energy sector analysis
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
        ├──► energy (Analysis)
        │        │
        │        └──► Client reports & dashboards
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
    ├──► energy (Data processing utilities)
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

### SPARC Methodology

All repositories follow the SPARC development methodology:
- **S**pecification: Requirements definition
- **P**seudocode: Algorithm design
- **A**rchitecture: System design
- **R**efinement: TDD implementation
- **C**ompletion: Production-ready code

### Claude Flow Orchestration

- **54+ specialized agents** available for different tasks
- **Swarm coordination** with hierarchical, mesh, and adaptive topologies
- **Multi-model support**: Claude, OpenAI GPT, Google Gemini

### Key Agent Categories

| Category | Agents | Purpose |
|----------|--------|---------|
| **Core** | coder, reviewer, tester, planner, researcher | Development |
| **SPARC** | specification, pseudocode, architecture, refinement | Methodology |
| **GitHub** | pr-manager, code-review-swarm, issue-tracker | Git workflows |
| **Specialized** | backend-dev, ml-developer, cicd-engineer | Domain-specific |

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
| Central configuration | `workspace-hub/CLAUDE.md` |
| Documentation index | `workspace-hub/docs/README.md` |
| AI guidelines | `workspace-hub/docs/modules/ai/AI_AGENT_GUIDELINES.md` |
| Development workflow | `workspace-hub/docs/modules/workflow/DEVELOPMENT_WORKFLOW.md` |
| Product mission | `workspace-hub/.agent-os/product/mission.md` |
| Tech stack | `workspace-hub/.agent-os/product/tech-stack.md` |
| Skills library | `workspace-hub/.claude/skills/` |

### Understanding a Repository

When working with any repository:

1. **Read CLAUDE.md** first (repo-specific configuration)
2. **Check .agent-os/** for product context (if exists)
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

All repositories are located under:
```
/mnt/github/workspace-hub/
```

### Finding a Repository

```bash
# List all repositories
ls -d /mnt/github/workspace-hub/*/

# Find repository by name
ls -d /mnt/github/workspace-hub/*model*/

# Check if repo exists
[ -d /mnt/github/workspace-hub/digitalmodel ] && echo "exists"
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

---

*This document is part of the workspace-hub documentation infrastructure. For updates, see the docs/ directory.*
