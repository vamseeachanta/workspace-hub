# Claude Code Skills Library

> User-level skills for Claude Code, accessible across all projects.
>
> Location: `~/.claude/skills/` (symlinked to `/mnt/github/workspace-hub/.claude/skills/`)
>
> Last Updated: 2026-01-02
> Template Version: 2.0.0

## Overview

This collection provides **98 specialized skills** organized into **8 categories** (plus 15 repo-specific). Skills are triggered automatically based on their description field when Claude Code determines they're relevant to the current task.

**Total Skills: 113** (98 central + 15 repo-specific)

## Quick Reference

| Category | Skills | Purpose |
|----------|--------|---------|
| [Document Handling](#document-handling) | 10 | PDF, DOCX, PPTX, XLSX, OCR, RAG, knowledge bases, semantic search |
| [Development](#development) | 33 | MCP, testing, SPARC, GitHub, planning, reports, workflows, pipelines |
| [Content & Design](#content--design) | 4 | Frontend UI, themes, canvas graphics, algorithmic art |
| [Communication](#communication) | 4 | Internal comms, Slack GIFs, document collaboration, branding |
| [Builders](#builders) | 2 | Web artifacts, skill creation |
| [Workspace Hub](#workspace-hub) | 32 | Core agents, swarm coordination, consensus, repository management, standards enforcement, automation |
| [Tools](#tools) | 17 | Optimization, cloud platform, AI assessment, background services |
| [Meta](#meta) | 1 | Session routines, skill maintenance |

**Repository-Specific Skills:**
- **digitalmodel**: 15 skills (engineering analysis, CAD, simulation)
- **worldenergydata**: 10 skills (energy data, production forecasting)

---

## Directory Structure

```
skills/
├── document-handling/       # PDF, DOCX, PPTX, XLSX, OCR, RAG, knowledge bases (10)
├── development/             # Software development (33)
│   ├── mcp-builder/
│   ├── webapp-testing/
│   ├── engineering-report-generator/
│   ├── yaml-workflow-executor/
│   ├── data-pipeline-processor/
│   ├── parallel-file-processor/
│   ├── git-worktree-workflow/
│   ├── github/              # GitHub integration skills (13) NEW
│   ├── sparc/               # SPARC methodology skills (4) NEW
│   ├── planning/            # Goal planning skills (2) NEW
│   └── testing/             # Testing skills (2) NEW
├── content-design/          # UI, themes, graphics, generative art (4)
├── communication/           # Business communications (4)
├── builders/                # Meta-tools for creation (2)
├── workspace-hub/           # Workspace ecosystem (25)
│   ├── repo-sync/
│   ├── sparc-workflow/
│   ├── agent-orchestration/
│   ├── compliance-check/
│   ├── workspace-cli/
│   ├── core/                # Core development agents (5) NEW
│   ├── swarm/               # Swarm coordination (8) NEW
│   └── consensus/           # Distributed consensus (7) NEW
├── tools/                   # Utilities (17)
│   ├── ai-tool-assessment/
│   ├── background-service-manager/
│   ├── optimization/        # Performance optimization (6) NEW
│   └── cloud/               # Flow-Nexus cloud platform (9) NEW
├── meta/                    # Skills about skills (1)
└── README.md
```

---

## Skills by Category

### Document Handling (10)

Work with business documents - reading, creating, editing, analyzing, and building searchable knowledge bases.

| Skill | Description |
|-------|-------------|
| [pdf](document-handling/pdf/SKILL.md) | Read, summarize, extract, and analyze PDF documents |
| [docx](document-handling/docx/SKILL.md) | Create and edit Word documents with formatting |
| [pptx](document-handling/pptx/SKILL.md) | Build PowerPoint presentations with slides and layouts |
| [xlsx](document-handling/xlsx/SKILL.md) | Generate Excel spreadsheets with formulas and charts |
| [document-rag-pipeline](document-handling/document-rag-pipeline/SKILL.md) | Complete RAG pipeline - PDF extraction, OCR, embeddings, semantic search |
| [pdf-text-extractor](document-handling/pdf-text-extractor/SKILL.md) | Extract text from PDFs (regular and OCR) |
| [knowledge-base-builder](document-handling/knowledge-base-builder/SKILL.md) | Build document inventories with SQLite catalogs |
| [semantic-search-setup](document-handling/semantic-search-setup/SKILL.md) | Generate vector embeddings for semantic search |
| [rag-system-builder](document-handling/rag-system-builder/SKILL.md) | Add LLM-powered Q&A to document collections (v1.2.0) |
| [document-inventory](document-handling/document-inventory/SKILL.md) | Build and manage document inventories with catalogs |

### Development (33)

Tools for building software - MCP servers, web testing, SPARC methodology, GitHub integration, planning, testing.

#### Core Development (7)

| Skill | Description |
|-------|-------------|
| [mcp-builder](development/mcp-builder/SKILL.md) | Build Model Context Protocol servers with Claude integration (v1.2.0) |
| [webapp-testing](development/webapp-testing/SKILL.md) | Test web applications with Playwright and Chrome DevTools |
| [engineering-report-generator](development/engineering-report-generator/SKILL.md) | Generate interactive HTML reports with Plotly visualizations |
| [yaml-workflow-executor](development/yaml-workflow-executor/SKILL.md) | Execute configuration-driven analysis workflows from YAML files |
| [data-pipeline-processor](development/data-pipeline-processor/SKILL.md) | Build ETL pipelines with validation, transformation, and reporting |
| [parallel-file-processor](development/parallel-file-processor/SKILL.md) | Process multiple files in parallel with aggregation and progress tracking |
| [git-worktree-workflow](development/git-worktree-workflow/SKILL.md) | Use git worktrees for parallel Claude workflows |

#### GitHub Integration (13) - NEW

| Skill | Description |
|-------|-------------|
| [github-pr-manager](development/github/github-pr-manager/SKILL.md) | Comprehensive PR management with swarm coordination |
| [github-code-review](development/github/github-code-review/SKILL.md) | Automated code review with multiple agents |
| [github-issue-tracker](development/github/github-issue-tracker/SKILL.md) | Issue triage and management |
| [github-release-manager](development/github/github-release-manager/SKILL.md) | Release coordination and versioning |
| [github-release-swarm](development/github/github-release-swarm/SKILL.md) | Multi-agent release automation |
| [github-repo-architect](development/github/github-repo-architect/SKILL.md) | Repository structure and design |
| [github-multi-repo](development/github/github-multi-repo/SKILL.md) | Cross-repository coordination |
| [github-sync](development/github/github-sync/SKILL.md) | Repository synchronization |
| [github-workflow](development/github/github-workflow/SKILL.md) | GitHub Actions automation |
| [github-project-board](development/github/github-project-board/SKILL.md) | GitHub Projects integration |
| [github-modes](development/github/github-modes/SKILL.md) | Multi-mode GitHub integration |
| [github-swarm-pr](development/github/github-swarm-pr/SKILL.md) | PR-based swarm coordination |
| [github-swarm-issue](development/github/github-swarm-issue/SKILL.md) | Issue-based swarm coordination |

#### SPARC Methodology (4) - NEW

| Skill | Description |
|-------|-------------|
| [sparc-specification](development/sparc/sparc-specification/SKILL.md) | Requirements analysis and specification writing |
| [sparc-pseudocode](development/sparc/sparc-pseudocode/SKILL.md) | Algorithm design and pseudocode generation |
| [sparc-architecture](development/sparc/sparc-architecture/SKILL.md) | System architecture design |
| [sparc-refinement](development/sparc/sparc-refinement/SKILL.md) | TDD implementation and code refinement |

#### Planning (2) - NEW

| Skill | Description |
|-------|-------------|
| [planning-goal](development/planning/planning-goal/SKILL.md) | Goal-Oriented Action Planning (GOAP) for complex objectives |
| [planning-code-goal](development/planning/planning-code-goal/SKILL.md) | Code-centric goal planning for software development |

#### Testing (2) - NEW

| Skill | Description |
|-------|-------------|
| [testing-tdd-london](development/testing/testing-tdd-london/SKILL.md) | TDD London School methodology with mocks |
| [testing-production](development/testing/testing-production/SKILL.md) | Production environment validation |

### Content & Design (4)

Create visual content - UI components, design systems, diagrams, and generative art.

| Skill | Description |
|-------|-------------|
| [frontend-design](content-design/frontend-design/SKILL.md) | Design and implement modern web UI components |
| [theme-factory](content-design/theme-factory/SKILL.md) | Create comprehensive design systems and themes |
| [canvas-design](content-design/canvas-design/SKILL.md) | Create diagrams, graphics, and visualizations with canvas |
| [algorithmic-art](content-design/algorithmic-art/SKILL.md) | Generate algorithmic and generative art with code |

### Communication (4)

Business communications - internal memos, Slack engagement, collaborative editing, brand identity.

| Skill | Description |
|-------|-------------|
| [internal-comms](communication/internal-comms/SKILL.md) | Craft professional internal business communications |
| [slack-gif-creator](communication/slack-gif-creator/SKILL.md) | Create custom animated GIFs for Slack |
| [doc-coauthoring](communication/doc-coauthoring/SKILL.md) | Collaborate on documents with tracked changes |
| [brand-guidelines](communication/brand-guidelines/SKILL.md) | Create and maintain brand guidelines |

### Builders (2)

Meta-tools for creating things - interactive web applications and new skills.

| Skill | Description |
|-------|-------------|
| [web-artifacts-builder](builders/web-artifacts-builder/SKILL.md) | Build self-contained interactive web applications |
| [skill-creator](builders/skill-creator/SKILL.md) | Create new Claude Code skills |

### Workspace Hub (32)

Specialized for workspace-hub ecosystem - repository management, development methodology, AI orchestration, swarm coordination, consensus protocols, standards enforcement, and automation.

#### Core Workspace (5)

| Skill | Description |
|-------|-------------|
| [repo-sync](workspace-hub/repo-sync/SKILL.md) | Manage and synchronize 26+ Git repositories |
| [sparc-workflow](workspace-hub/sparc-workflow/SKILL.md) | Apply SPARC methodology for systematic development |
| [agent-orchestration](workspace-hub/agent-orchestration/SKILL.md) | Orchestrate AI agents with Claude Flow swarms |
| [compliance-check](workspace-hub/compliance-check/SKILL.md) | Verify coding standards and workspace compliance |
| [workspace-cli](workspace-hub/workspace-cli/SKILL.md) | Use the unified workspace-hub CLI |

#### Core Development Agents (5) - NEW

| Skill | Description |
|-------|-------------|
| [core-coder](workspace-hub/core/core-coder/SKILL.md) | Implementation specialist for writing clean, efficient code |
| [core-reviewer](workspace-hub/core/core-reviewer/SKILL.md) | Code review and quality assurance |
| [core-tester](workspace-hub/core/core-tester/SKILL.md) | Testing and test automation |
| [core-planner](workspace-hub/core/core-planner/SKILL.md) | Project planning and task breakdown |
| [core-researcher](workspace-hub/core/core-researcher/SKILL.md) | Research and information gathering |

#### Swarm Coordination (8) - NEW

| Skill | Description |
|-------|-------------|
| [swarm-hierarchical](workspace-hub/swarm/swarm-hierarchical/SKILL.md) | Queen-led hierarchical swarm coordination |
| [swarm-mesh](workspace-hub/swarm/swarm-mesh/SKILL.md) | Peer-to-peer mesh network coordination |
| [swarm-adaptive](workspace-hub/swarm/swarm-adaptive/SKILL.md) | Dynamic topology switching and optimization |
| [swarm-queen](workspace-hub/swarm/swarm-queen/SKILL.md) | Central orchestrator for swarm operations |
| [swarm-collective](workspace-hub/swarm/swarm-collective/SKILL.md) | Collective intelligence coordination |
| [swarm-memory](workspace-hub/swarm/swarm-memory/SKILL.md) | Distributed memory management |
| [swarm-scout](workspace-hub/swarm/swarm-scout/SKILL.md) | Information reconnaissance and exploration |
| [swarm-worker](workspace-hub/swarm/swarm-worker/SKILL.md) | Dedicated task execution specialist |

#### Consensus/Distributed (7) - NEW

| Skill | Description |
|-------|-------------|
| [consensus-byzantine](workspace-hub/consensus/consensus-byzantine/SKILL.md) | Byzantine fault-tolerant consensus |
| [consensus-raft](workspace-hub/consensus/consensus-raft/SKILL.md) | Raft consensus with leader election |
| [consensus-gossip](workspace-hub/consensus/consensus-gossip/SKILL.md) | Gossip-based eventual consistency |
| [consensus-crdt](workspace-hub/consensus/consensus-crdt/SKILL.md) | Conflict-free replicated data types |
| [consensus-quorum](workspace-hub/consensus/consensus-quorum/SKILL.md) | Quorum-based voting systems |
| [consensus-security](workspace-hub/consensus/consensus-security/SKILL.md) | Security validation and enforcement |
| [consensus-benchmark](workspace-hub/consensus/consensus-benchmark/SKILL.md) | Consensus performance benchmarking |

#### Standards & Automation (7) - NEW

| Skill | Description |
|-------|-------------|
| [knowledge-base-system](workspace-hub/knowledge-base-system/SKILL.md) | Centralized knowledge base with multi-dimensional indexing and pattern recognition |
| [development-workflow-orchestrator](workspace-hub/development-workflow-orchestrator/SKILL.md) | Automate 6-phase YAML-driven development workflow |
| [ai-questioning-pattern](workspace-hub/ai-questioning-pattern/SKILL.md) | MANDATORY questioning pattern before implementation |
| [html-reporting-enforcer](workspace-hub/html-reporting-enforcer/SKILL.md) | Enforce interactive-only HTML reporting standards |
| [file-organization-assistant](workspace-hub/file-organization-assistant/SKILL.md) | AI-driven file organization with 5+ file trigger |
| [compliance-propagation-automator](workspace-hub/compliance-propagation-automator/SKILL.md) | Automate standards propagation across all repositories |
| [repository-health-analyzer](workspace-hub/repository-health-analyzer/SKILL.md) | 100-point health scoring across 5 dimensions |

### Tools (17)

Assessment, optimization, and cloud platform utilities.

#### Core Tools (2)

| Skill | Description |
|-------|-------------|
| [ai-tool-assessment](tools/ai-tool-assessment/SKILL.md) | Assess AI tool subscriptions, usage, and cost-effectiveness |
| [background-service-manager](tools/background-service-manager/SKILL.md) | Manage background services and daemons |

#### Performance Optimization (6) - NEW

| Skill | Description |
|-------|-------------|
| [optimization-monitor](tools/optimization/optimization-monitor/SKILL.md) | Real-time performance monitoring |
| [optimization-benchmark](tools/optimization/optimization-benchmark/SKILL.md) | Performance benchmarking suite |
| [optimization-load-balancer](tools/optimization/optimization-load-balancer/SKILL.md) | Task distribution and load balancing |
| [optimization-resources](tools/optimization/optimization-resources/SKILL.md) | Resource allocation and management |
| [optimization-topology](tools/optimization/optimization-topology/SKILL.md) | Network topology optimization |
| [optimization-analyzer](tools/optimization/optimization-analyzer/SKILL.md) | Performance bottleneck analysis |

#### Flow-Nexus Cloud Platform (9) - NEW

| Skill | Description |
|-------|-------------|
| [cloud-swarm](tools/cloud/cloud-swarm/SKILL.md) | Cloud-based swarm orchestration |
| [cloud-neural](tools/cloud/cloud-neural/SKILL.md) | Neural network training and deployment |
| [cloud-sandbox](tools/cloud/cloud-sandbox/SKILL.md) | E2B sandbox management |
| [cloud-workflow](tools/cloud/cloud-workflow/SKILL.md) | Event-driven workflow automation |
| [cloud-app-store](tools/cloud/cloud-app-store/SKILL.md) | Application marketplace |
| [cloud-auth](tools/cloud/cloud-auth/SKILL.md) | Authentication and user management |
| [cloud-payments](tools/cloud/cloud-payments/SKILL.md) | Credit management and billing |
| [cloud-challenges](tools/cloud/cloud-challenges/SKILL.md) | Coding challenges and gamification |
| [cloud-user-tools](tools/cloud/cloud-user-tools/SKILL.md) | User utilities and Seraphina |

### Meta (1)

Skills about skills - maintenance, creation, and session management.

| Skill | Description |
|-------|-------------|
| [session-start-routine](meta/session-start-routine/SKILL.md) | Session initialization routine for skill maintenance (v2.0.0) |

---

## Repository-Specific Skills

### digitalmodel (15)

| Skill | Description |
|-------|-------------|
| [orcaflex-modeling](../../digitalmodel/.claude/skills/orcaflex-modeling/SKILL.md) | OrcaFlex simulation setup and running (v2.0.0) |
| [orcaflex-post-processing](../../digitalmodel/.claude/skills/orcaflex-post-processing/SKILL.md) | OrcaFlex results post-processing |
| [aqwa-analysis](../../digitalmodel/.claude/skills/aqwa-analysis/SKILL.md) | AQWA hydrodynamic analysis (v3.0.0) |
| [orcawave-analysis](../../digitalmodel/.claude/skills/orcawave-analysis/SKILL.md) | Wave spectrum generation and analysis - NEW |
| [freecad-automation](../../digitalmodel/.claude/skills/freecad-automation/SKILL.md) | FreeCAD CAD automation - NEW |
| [gmsh-meshing](../../digitalmodel/.claude/skills/gmsh-meshing/SKILL.md) | Mesh generation for simulations - NEW |
| [cad-engineering](../../digitalmodel/.claude/skills/cad-engineering/SKILL.md) | CAD expertise and format conversions - NEW |
| [cathodic-protection](../../digitalmodel/.claude/skills/cathodic-protection/SKILL.md) | Cathodic protection systems - NEW |
| [fatigue-analysis](../../digitalmodel/.claude/skills/fatigue-analysis/SKILL.md) | S-N curves, damage accumulation |
| [mooring-design](../../digitalmodel/.claude/skills/mooring-design/SKILL.md) | CALM/SALM buoy analysis |
| [structural-analysis](../../digitalmodel/.claude/skills/structural-analysis/SKILL.md) | Stress, buckling, capacity checks |
| [catenary-riser](../../digitalmodel/.claude/skills/catenary-riser/SKILL.md) | Catenary riser design |
| [hydrodynamics](../../digitalmodel/.claude/skills/hydrodynamics/SKILL.md) | Hydrodynamic calculations |
| [signal-analysis](../../digitalmodel/.claude/skills/signal-analysis/SKILL.md) | Signal processing and analysis |
| [viv-analysis](../../digitalmodel/.claude/skills/viv-analysis/SKILL.md) | Vortex-induced vibration analysis |

### worldenergydata (10)

| Skill | Description |
|-------|-------------|
| [bsee-data-extractor](../../worldenergydata/.claude/skills/bsee-data-extractor/SKILL.md) | BSEE production data extraction |
| [energy-data-visualizer](../../worldenergydata/.claude/skills/energy-data-visualizer/SKILL.md) | Energy data visualization |
| [fdas-economics](../../worldenergydata/.claude/skills/fdas-economics/SKILL.md) | FDAS economics analysis |
| [field-analyzer](../../worldenergydata/.claude/skills/field-analyzer/SKILL.md) | Oil/gas field analysis |
| [marine-safety-incidents](../../worldenergydata/.claude/skills/marine-safety-incidents/SKILL.md) | Marine safety incident analysis |
| [npv-analyzer](../../worldenergydata/.claude/skills/npv-analyzer/SKILL.md) | NPV and economic evaluation |
| [production-forecaster](../../worldenergydata/.claude/skills/production-forecaster/SKILL.md) | Arps decline curves and EUR forecasting |
| [sodir-data-extractor](../../worldenergydata/.claude/skills/sodir-data-extractor/SKILL.md) | SODIR (Norwegian) data extraction |
| [web-scraper-energy](../../worldenergydata/.claude/skills/web-scraper-energy/SKILL.md) | Energy website scraping |
| [well-production-dashboard](../../worldenergydata/.claude/skills/well-production-dashboard/SKILL.md) | Well production dashboards |

---

## Skill Template v2.0

All skills follow [SKILL_TEMPLATE_v2.md](../../docs/SKILL_TEMPLATE_v2.md) format:

```yaml
---
name: skill-name
description: Trigger description for auto-detection
version: 1.0.0
category: development|workspace-hub|tools|etc
related_skills:
  - related-skill-1
  - related-skill-2
---
```

Required sections:
- Quick Start
- When to Use
- Core Concepts
- Usage Examples
- Best Practices
- Error Handling
- Version History

---

## Usage

### Automatic Activation

Skills activate automatically when Claude Code determines they're relevant:

```
User: "Create a PDF summary of this document"
Claude: [Activates pdf skill, provides PDF processing guidance]

User: "Initialize a hierarchical swarm for code review"
Claude: [Activates swarm-hierarchical skill, provides swarm coordination]
```

### Manual Invocation

Reference skills directly in prompts:

```
"Using the sparc-workflow skill, help me plan this feature"
"Apply the consensus-raft skill to implement leader election"
```

---

## Installation Verification

```bash
# Verify symlink
ls -la ~/.claude/skills

# Count all skills
find ~/.claude/skills -name "SKILL.md" | wc -l
# Expected: 98

# List categories
ls ~/.claude/skills/

# Check specific skill
cat ~/.claude/skills/workspace-hub/swarm/swarm-hierarchical/SKILL.md
```

---

## Related Documentation

- [SKILL_TEMPLATE_v2.md](../../docs/SKILL_TEMPLATE_v2.md) - Skill template standard
- [AGENT_TO_SKILL_CONVERSION.md](../../docs/AGENT_TO_SKILL_CONVERSION.md) - Conversion tracking
- [Claude Code Skills Documentation](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Anthropic Official Skills](https://github.com/anthropics/skills)
- [AI Agent Guidelines](../../docs/modules/ai/AI_AGENT_GUIDELINES.md)

---

## Changelog

### 2026-01-05 - Standards & Automation Skills

**New Skills (7):**
- `workspace-hub/knowledge-base-system` - Multi-dimensional knowledge base with pattern recognition
- `workspace-hub/development-workflow-orchestrator` - 6-phase YAML-driven workflow automation
- `workspace-hub/ai-questioning-pattern` - MANDATORY questioning before implementation
- `workspace-hub/html-reporting-enforcer` - Interactive-only HTML reporting standards
- `workspace-hub/file-organization-assistant` - AI-driven file organization (5+ file trigger)
- `workspace-hub/compliance-propagation-automator` - Standards sync across 26+ repositories
- `workspace-hub/repository-health-analyzer` - 100-point health scoring system

**Total Skills:** 113 (98 central + 15 repo-specific)
- Workspace Hub expanded from 25 to 32 skills

### 2026-01-02 - Major Agent-to-Skill Conversion

**New Skills (56):**
- `workspace-hub/core/` (5) - Core development agents
- `workspace-hub/swarm/` (8) - Swarm coordination
- `workspace-hub/consensus/` (7) - Distributed consensus
- `development/github/` (13) - GitHub integration
- `development/sparc/` (4) - SPARC methodology
- `development/planning/` (2) - Goal planning
- `development/testing/` (2) - Testing skills
- `tools/optimization/` (6) - Performance optimization
- `tools/cloud/` (9) - Flow-Nexus cloud platform

**Upgraded Skills (35):**
- All existing skills upgraded to v2.0 template format
- Added: Quick Start, When to Use, Execution Checklist, Error Handling, Metrics sections

**digitalmodel Repository (5 new):**
- `orcawave-analysis` - Wave spectrum generation
- `freecad-automation` - FreeCAD CAD automation
- `gmsh-meshing` - Mesh generation
- `cad-engineering` - CAD engineering specialist
- `cathodic-protection` - Cathodic protection systems

### 2025-12-30

**New Skills:**
- `meta/session-start-routine` (v1.0.0) - Session initialization routine
- `development/git-worktree-workflow` (v1.0.0) - Parallel Claude workflows

**Updated Skills:**
- `development/mcp-builder` (v1.1.0) - Added .mcp.json, wildcards, security
- `document-handling/rag-system-builder` (v1.1.0) - Added hybrid search, reranking

---

*Skills are user-level and available across all projects via symlink at `~/.claude/skills/`*
