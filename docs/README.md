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
│
├── ai/                              # AI agent & Claude documentation
│   ├── AI_AGENT_GUIDELINES.md       # AI agent workflow rules (MANDATORY)
│   ├── AI_USAGE_GUIDELINES.md       # AI effectiveness patterns
│   ├── AI_HELPER_EXAMPLES.md        # Example interactions
│   ├── AI_development_tools.md      # AI tools & memberships
│   ├── INTERACTIVE_MODE_GUIDELINES.md
│   ├── MCP_SETUP_GUIDE.md           # MCP server configuration
│   ├── CLAUDE_INTERACTION_GUIDE.md
│   ├── CLAUDE_PROJECT_MEMORY.md
│   ├── CLAUDE_RULES_*.md            # Claude configuration guides
│   └── ...
│
├── workflow/                        # Development workflow documentation
│   ├── DEVELOPMENT_WORKFLOW.md      # Main workflow guide
│   ├── DEVELOPMENT_WORKFLOW_GUIDELINES.md
│   ├── DEVELOPMENT_WORKFLOW_SUMMARY.md
│   └── IMPLEMENTATION_ROADMAP.md
│
├── standards/                       # Standards & compliance
│   ├── FILE_ORGANIZATION_STANDARDS.md
│   ├── LOGGING_STANDARDS.md
│   ├── TESTING_FRAMEWORK_STANDARDS.md
│   ├── HTML_REPORTING_STANDARDS.md
│   ├── COMPLIANCE_ENFORCEMENT.md
│   └── README_COMPLIANCE.md
│
├── cli/                             # CLI & tools documentation
│   ├── WORKSPACE_CLI.md             # Main CLI guide
│   ├── CLI_MENU_STRUCTURE.md
│   ├── MENU_VISUAL_GUIDE.md
│   ├── SCRIPT_ORGANIZATION.md
│   └── REPOSITORY_SYNC.md
│
├── modules/                         # Module-specific documentation
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

1. 📋 [AI Agent Guidelines](ai/AI_AGENT_GUIDELINES.md) - **HIGHEST PRIORITY**
2. 💡 [AI Usage Guidelines](ai/AI_USAGE_GUIDELINES.md) - Effectiveness patterns
3. 🔧 [MCP Setup Guide](ai/MCP_SETUP_GUIDE.md) - MCP server configuration

### Getting Started

- 🚀 [Workspace Hub Capabilities](WORKSPACE_HUB_CAPABILITIES_SUMMARY.md)
- 📋 [Development Workflow](workflow/DEVELOPMENT_WORKFLOW.md)
- 🤖 [Claude Interaction Guide](ai/CLAUDE_INTERACTION_GUIDE.md)
- 📖 [Implementation Roadmap](workflow/IMPLEMENTATION_ROADMAP.md)

### Standards & Compliance

- 📁 [File Organization Standards](standards/FILE_ORGANIZATION_STANDARDS.md)
- 📝 [Logging Standards](standards/LOGGING_STANDARDS.md)
- ✅ [Testing Framework Standards](standards/TESTING_FRAMEWORK_STANDARDS.md)
- 📊 [HTML Reporting Standards](standards/HTML_REPORTING_STANDARDS.md)
- 🔒 [Compliance Enforcement](standards/COMPLIANCE_ENFORCEMENT.md)

### CLI & Tools

- 💻 [Workspace CLI](cli/WORKSPACE_CLI.md)
- 📋 [CLI Menu Structure](cli/CLI_MENU_STRUCTURE.md)
- 🔄 [Repository Sync](cli/REPOSITORY_SYNC.md)
- 📦 [Script Organization](cli/SCRIPT_ORGANIZATION.md)

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
| AI Agents | [ai/](ai/) | AI_AGENT_GUIDELINES.md, AI_USAGE_GUIDELINES.md |
| Development Workflow | [workflow/](workflow/) | DEVELOPMENT_WORKFLOW.md |
| Standards | [standards/](standards/) | FILE_ORGANIZATION_STANDARDS.md |
| CLI Tools | [cli/](cli/) | WORKSPACE_CLI.md |
| Testing | [modules/testing/](modules/testing/) | baseline-testing-standards.md |
| CI/CD | [modules/ci-cd/](modules/ci-cd/) | cicd-integration-workflows.md |
| Monitoring | [modules/monitoring/](modules/monitoring/) | metrics-collection-framework.md |

### By Task

| Task | Documentation |
|------|--------------|
| Configure AI agents | [ai/AI_AGENT_GUIDELINES.md](ai/AI_AGENT_GUIDELINES.md) |
| Setup development workflow | [workflow/DEVELOPMENT_WORKFLOW.md](workflow/DEVELOPMENT_WORKFLOW.md) |
| Configure CI/CD | [modules/ci-cd/ci-cd-baseline-integration.md](modules/ci-cd/ci-cd-baseline-integration.md) |
| Add testing | [modules/testing/testing-templates/](modules/testing/testing-templates/) |
| Install UV | [modules/environment/uv-modernization-plan.md](modules/environment/uv-modernization-plan.md) |
| Setup monitoring | [modules/monitoring/metrics-collection-framework.md](modules/monitoring/metrics-collection-framework.md) |
| Use workspace CLI | [cli/WORKSPACE_CLI.md](cli/WORKSPACE_CLI.md) |

## Directory Reference

### Repository Structure
```
workspace-hub/
├── .agent-os/              # Agent OS configuration
│   └── product/            # Product docs (mission, tech-stack, roadmap, decisions)
├── docs/                   # THIS DOCUMENTATION
│   ├── ai/                 # AI agent documentation
│   ├── workflow/           # Development workflow
│   ├── standards/          # Standards & compliance
│   ├── cli/                # CLI documentation
│   └── modules/            # Module-specific docs
├── specs/                  # Feature specifications
├── modules/                # Functional modules (workspace-level)
├── scripts/                # Automation scripts
├── config/                 # Configuration files
├── templates/              # Document & config templates
└── README.md               # Main repository README
```

## Contributing to Documentation

### Documentation Standards
- ✅ Use **organized subdirectories** (ai/, workflow/, standards/, cli/, modules/)
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

*Last Updated: 2025-12-22*
*Part of the workspace-hub documentation infrastructure*
