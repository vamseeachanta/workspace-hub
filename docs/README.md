# Workspace-Hub Documentation

Comprehensive documentation for the workspace-hub multi-repository management system.

## Overview

Workspace-hub is a centralized repository management system that helps development teams collaborate across 26+ independent Git repositories by providing unified automation, synchronization, and orchestration tools through a modular architecture.

**This documentation serves as the central reference for all repositories in the workspace.**

## Documentation Structure

```
docs/
├── README.md                        # This file - main index
├── WORKSPACE_HUB_CAPABILITIES_SUMMARY.md  # Full capabilities overview
├── WORKSPACE_HUB_REPOSITORY_OVERVIEW.md   # Repository relationships & navigation
│
├── modules/                         # All module documentation
│   ├── ai/                          # AI agent & Claude documentation
│   │   ├── AI_AGENT_GUIDELINES.md   # AI agent workflow rules (MANDATORY)
│   │   ├── AI_USAGE_GUIDELINES.md   # AI effectiveness patterns
│   │   ├── AI_HELPER_EXAMPLES.md    # Example interactions
│   │   ├── MCP_SETUP_GUIDE.md       # MCP server configuration
│   │   ├── CLAUDE_INTERACTION_GUIDE.md
│   │   ├── agent-patterns/          # Agent organization & conversion guides
│   │   └── skills/                  # Skill deployment & templates
│   │
│   ├── workflow/                    # Development workflow documentation
│   │   ├── DEVELOPMENT_WORKFLOW.md  # Main workflow guide
│   │   ├── DEVELOPMENT_WORKFLOW_GUIDELINES.md
│   │   └── IMPLEMENTATION_ROADMAP.md
│   │
│   ├── standards/                   # Standards & compliance
│   │   ├── FILE_ORGANIZATION_STANDARDS.md
│   │   ├── LOGGING_STANDARDS.md
│   │   ├── TESTING_FRAMEWORK_STANDARDS.md
│   │   ├── HTML_REPORTING_STANDARDS.md
│   │   └── COMPLIANCE_ENFORCEMENT.md
│   │
│   ├── cli/                         # CLI & tools documentation
│   │   ├── WORKSPACE_CLI.md         # Main CLI guide
│   │   ├── CLI_MENU_STRUCTURE.md
│   │   └── REPOSITORY_SYNC.md
│   │
│   ├── repository/                  # Repository management
│   │   ├── REPOSITORY_ANALYSIS_RECOMMENDATIONS.md
│   │   ├── REPOSITORY_IMPROVEMENT_TRACKER.md
│   │   └── SELF_IMPROVING_REPOSITORIES_FRAMEWORK.md
│   │
│   ├── tiers/                       # Repository tier assessments
│   │   ├── TIER2_ASSESSMENT_DEPLOYMENT_PLAN.md
│   │   ├── TIER2_REPOSITORY_INDEX.md
│   │   └── TIER_3_MINIMAL_ASSESSMENT.md
│   │
│   ├── archive/                     # Archived documentation
│   │
│   ├── ai-native/                   # AI-native infrastructure
│   ├── automation/                  # AI agent orchestration
│   ├── testing/                     # Testing infrastructure
│   ├── ci-cd/                       # CI/CD pipelines
│   ├── environment/                 # UV environment management
│   ├── architecture/                # System architecture
│   └── monitoring/                  # Monitoring & metrics
│
├── api/                             # API documentation (future)
└── pseudocode/                      # Pseudocode for implementations
```

## Quick Links

### 🚨 AI Agents - Start Here (MANDATORY)

**All AI agents (Claude, OpenAI, Factory.ai) MUST read these first:**

1. 📋 [AI Agent Guidelines](modules/ai/AI_AGENT_GUIDELINES.md) - **HIGHEST PRIORITY**
2. 💡 [AI Usage Guidelines](modules/ai/AI_USAGE_GUIDELINES.md) - Effectiveness patterns
3. 🔧 [MCP Setup Guide](modules/ai/MCP_SETUP_GUIDE.md) - MCP server configuration

### Getting Started

- 🗺️ [Repository Overview](WORKSPACE_HUB_REPOSITORY_OVERVIEW.md) - **Repository relationships & navigation**
- 🚀 [Workspace Hub Capabilities](WORKSPACE_HUB_CAPABILITIES_SUMMARY.md)
- 📋 [Development Workflow](modules/workflow/DEVELOPMENT_WORKFLOW.md)
- 🤖 [Claude Interaction Guide](modules/ai/CLAUDE_INTERACTION_GUIDE.md)
- 🗓️ [Weekly Ecosystem Execution & Intelligence Review](modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md)
- 📖 [Implementation Roadmap](modules/workflow/IMPLEMENTATION_ROADMAP.md)

### Standards & Compliance

- [AI Review Routing Policy](standards/AI_REVIEW_ROUTING_POLICY.md) — provider roles, review defaults, Gemini trigger rules
- [Control-Plane Contract](standards/CONTROL_PLANE_CONTRACT.md) — canonical entry points and provider adapters
- 📁 [File Organization Standards](modules/standards/FILE_ORGANIZATION_STANDARDS.md)
- 📝 [Logging Standards](modules/standards/LOGGING_STANDARDS.md)
- ✅ [Testing Framework Standards](modules/standards/TESTING_FRAMEWORK_STANDARDS.md)
- 📊 [HTML Reporting Standards](modules/standards/HTML_REPORTING_STANDARDS.md)
- 🔒 [Compliance Enforcement](modules/standards/COMPLIANCE_ENFORCEMENT.md)

### CLI & Tools

- 💻 [Workspace CLI](modules/cli/WORKSPACE_CLI.md)
- 📋 [CLI Menu Structure](modules/cli/CLI_MENU_STRUCTURE.md)
- 🔄 [Repository Sync](modules/cli/REPOSITORY_SYNC.md)
- 📦 [Script Organization](modules/cli/SCRIPT_ORGANIZATION.md)

## Knowledge & Intelligence Ecosystem

The workspace-hub contains a large-scale intelligence ecosystem spanning domain knowledge, document registries, and engineering documentation.

| Asset | Location | Scale |
|---|---|---|
| **Intelligence landing page** | [document-intelligence/](document-intelligence/README.md) | Architecture, inventories, maps |
| **LLM-Wikis** | [knowledge/wikis/](../knowledge/wikis/) | 19,300+ pages across 5 domains |
| **Document registries** | [data-intelligence-map](document-intelligence/data-intelligence-map.md) | 1M+ indexed documents, 639K summaries |
| **Design code registry** | [data/design-codes/code-registry.yaml](../data/design-codes/code-registry.yaml) | ~30 engineering codes |
| **Weekly intelligence review** | [WEEKLY_ECOSYSTEM_...](modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md) | Operational health review |

For architecture and reading order, start at the [intelligence landing page](document-intelligence/README.md).

## Core Modules

### 🧠 [AI-Native](modules/ai-native/)
AI-native repository infrastructure, structure standards, and AI optimization.
- [Structure Review](modules/ai-native/ai-native-structure-review.md)
- [Gold Standard Summary](modules/ai-native/digitalmodel-gold-standard-summary.md)

### 🤖 [Automation](modules/automation/)
AI agent orchestration, swarm coordination, and automation workflows.
- [AI Agent Orchestration](modules/automation/AI_AGENT_ORCHESTRATION.md) - 54+ specialized agents
- [Factory AI Integration](modules/automation/FACTORY_AI_GUIDE.md)
- [Agent Centralization](modules/automation/AGENT_CENTRALIZATION_COMPLETE.md)

### ✅ [Testing](modules/testing/)
Testing infrastructure, standards, and templates for quality assurance.
- [Baseline Testing Standards](modules/testing/baseline-testing-standards.md)
- [Test System Architecture](modules/testing/test-baseline-system-architecture.md)
- [Testing Templates](modules/testing/testing-templates/)

### 🔄 [CI/CD](modules/ci-cd/)
Continuous integration and deployment pipelines.
- [CI/CD Baseline Integration](modules/ci-cd/ci-cd-baseline-integration.md)
- [Workflow Patterns](modules/ci-cd/cicd-integration-workflows.md)

### 🐍 [Environment](modules/environment/)
Python environment management with UV package manager.
- [UV Modernization Plan](modules/environment/uv-modernization-plan.md)
- [UV Strategy](modules/environment/uv-modernization-strategy.md)
- [UV Templates](modules/environment/uv-templates/)

### 🏗️ [Architecture](modules/architecture/)
System architecture, design patterns, and infrastructure.
- [API Layer & Integrations](modules/architecture/api-layer-external-integrations.md)
- [Storage System](modules/architecture/baseline-storage-system.md)
- [Scalability Framework](modules/architecture/scalability-extensibility-framework.md)

### 📊 [Monitoring](modules/monitoring/)
Monitoring, metrics collection, and reporting systems.
- [Metrics Collection Framework](modules/monitoring/metrics-collection-framework.md)
- [Reporting & Notifications](modules/monitoring/reporting-notification-system.md)
- [Statistical Analysis](modules/monitoring/statistical-analysis-anomaly-detection.md)

### 📁 [Repository](modules/repository/)
Repository management, analysis, and self-improvement frameworks.
- [Repository Analysis Recommendations](modules/repository/REPOSITORY_ANALYSIS_RECOMMENDATIONS.md)
- [Repository Improvement Tracker](modules/repository/REPOSITORY_IMPROVEMENT_TRACKER.md)
- [Self-Improving Repositories Framework](modules/repository/SELF_IMPROVING_REPOSITORIES_FRAMEWORK.md)

### 🏷️ [Tiers](modules/tiers/)
Repository tier classification and assessment documentation.
- [Tier 2 Assessment Plan](modules/tiers/TIER2_ASSESSMENT_DEPLOYMENT_PLAN.md)
- [Tier 2 Repository Index](modules/tiers/TIER2_REPOSITORY_INDEX.md)
- [Tier 3 Minimal Assessment](modules/tiers/TIER_3_MINIMAL_ASSESSMENT.md)

### 🤖 AI Subdirectories
Additional AI-related documentation organized by topic:
- [Agent Patterns](modules/ai/agent-patterns/) - Agent organization and skill conversion guides
- [Skills](modules/ai/skills/) - Skill deployment, templates, and installation guides

### 📐 [Compound Engineering Methodology](methodology/)
Operational lessons from running production AI-augmented engineering workflows.

- [Compound Engineering](methodology/compound-engineering.md) — 5 operational lessons from production AI-augmented engineering
- [Enforcement Over Instruction](methodology/enforcement-over-instruction.md) — Why technical gates succeed where text-based rules fail
- [Multi-Agent Parity](methodology/multi-agent-parity.md) — How 4 AI agents share knowledge without redundant discovery
- [Orchestrator-Worker](methodology/orchestrator-worker.md) — Context isolation by separating planning from execution
- [Compliance Dashboard](methodology/compliance-dashboard.md) — Monitoring and enforcing AI agent workflow compliance
- [Cross-Review](methodology/cross-review.md) — Independent AI reviewers catching failures that self-review misses
- [Knowledge-to-Website Pipeline](methodology/knowledge-to-website-pipeline.md) — Converting repo knowledge into client-facing web content

## Key Features

### Multi-Repository Management
- **26+ repositories** managed with unified tooling
- **Independent workflows** maintained per repository
- **Centralized automation** with module-based architecture
- **Batch operations** for git, testing, and deployment

### AI Agent Orchestration
- **54+ specialized agents** for different tasks
- **SPARC methodology** (Specification, Pseudocode, Architecture, Refinement, Completion)
- **Swarm coordination** with hierarchical, mesh, and adaptive topologies
- **Multi-model support** (Claude, OpenAI GPT, Google Gemini)

### Development Workflow
- **user_prompt.md** → **YAML config** → **pseudocode** → **TDD** → **implementation**
- **Bash-based execution** for efficiency
- **Interactive engagement** with clarifying questions
- **Gate-pass reviews** at critical checkpoints

### Environment Management
- **UV package manager** for fast Python dependency resolution
- **Automated environment** setup across all repositories
- **Reproducible builds** with lock files

## Finding Documentation

### By Topic

| Topic | Location | Key Documents |
|-------|----------|---------------|
| AI Agents | [modules/ai/](modules/ai/) | AI_AGENT_GUIDELINES.md, AI_USAGE_GUIDELINES.md |
| Agent Patterns | [modules/ai/agent-patterns/](modules/ai/agent-patterns/) | AGENT_ORGANIZATION_GUIDE.md |
| Skills | [modules/ai/skills/](modules/ai/skills/) | SKILL_TEMPLATE_v2.md |
| Development Workflow | [modules/workflow/](modules/workflow/) | DEVELOPMENT_WORKFLOW.md |
| Standards | [modules/standards/](modules/standards/) | FILE_ORGANIZATION_STANDARDS.md |
| CLI Tools | [modules/cli/](modules/cli/) | WORKSPACE_CLI.md |
| Testing | [modules/testing/](modules/testing/) | baseline-testing-standards.md |
| CI/CD | [modules/ci-cd/](modules/ci-cd/) | cicd-integration-workflows.md |
| Monitoring | [modules/monitoring/](modules/monitoring/) | metrics-collection-framework.md |
| Repository | [modules/repository/](modules/repository/) | REPOSITORY_ANALYSIS_RECOMMENDATIONS.md |
| Tiers | [modules/tiers/](modules/tiers/) | TIER2_REPOSITORY_INDEX.md |

### By Task

| Task | Documentation |
|------|--------------|
| Configure AI agents | [modules/ai/AI_AGENT_GUIDELINES.md](modules/ai/AI_AGENT_GUIDELINES.md) |
| Setup development workflow | [modules/workflow/DEVELOPMENT_WORKFLOW.md](modules/workflow/DEVELOPMENT_WORKFLOW.md) |
| Configure CI/CD | [modules/ci-cd/ci-cd-baseline-integration.md](modules/ci-cd/ci-cd-baseline-integration.md) |
| Add testing | [modules/testing/testing-templates/](modules/testing/testing-templates/) |
| Install UV | [modules/environment/uv-modernization-plan.md](modules/environment/uv-modernization-plan.md) |
| Setup monitoring | [modules/monitoring/metrics-collection-framework.md](modules/monitoring/metrics-collection-framework.md) |
| Use workspace CLI | [modules/cli/WORKSPACE_CLI.md](modules/cli/WORKSPACE_CLI.md) |

## Directory Reference

### Repository Structure
```
workspace-hub/
├── .agent-os/              # Agent OS configuration
│   └── product/            # Product docs (mission, tech-stack, roadmap, decisions)
├── docs/                   # THIS DOCUMENTATION
│   └── modules/            # All module documentation
│       ├── ai/             # AI agent documentation
│       ├── workflow/       # Development workflow
│       ├── standards/      # Standards & compliance
│       ├── cli/            # CLI documentation
│       ├── testing/        # Testing infrastructure
│       ├── ci-cd/          # CI/CD pipelines
│       └── ...             # Other modules
├── specs/                  # Feature specifications
├── modules/                # Functional modules (workspace-level)
├── scripts/                # Automation scripts
├── config/                 # Configuration files
├── templates/              # Document & config templates
└── README.md               # Main repository README
```

## Contributing to Documentation

### Documentation Standards
- ✅ Use **organized subdirectories** under `modules/` (ai/, workflow/, standards/, cli/, testing/, etc.)
- ✅ Create **README.md** in each module directory
- ✅ Include **code examples** and **quick starts**
- ✅ Add **cross-references** to related documentation
- ✅ Update **this index** when adding new documents

### File Naming
- Use **UPPER_SNAKE_CASE** for standards/guidelines: `AI_AGENT_GUIDELINES.md`
- Use **kebab-case** for technical docs: `feature-name.md`
- Use **lowercase** for directories: `modules/ai-native/`

## Related Resources

### Product Documentation
- [Mission & Vision](../.agent-os/product/mission.md)
- [Technical Stack](../.agent-os/product/tech-stack.md)
- [Development Roadmap](../.agent-os/product/roadmap.md)
- [Product Decisions](../.agent-os/product/decisions.md)

### External Resources
- [Claude Flow Documentation](https://github.com/ruvnet/claude-flow)
- [UV Package Manager](https://github.com/astral-sh/uv)
- [Agent OS Framework](https://buildermethods.com/agent-os)

---

*Last Updated: 2026-01-24*
*Part of the workspace-hub documentation infrastructure*
