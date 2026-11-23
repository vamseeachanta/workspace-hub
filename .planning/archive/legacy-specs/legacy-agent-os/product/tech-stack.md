# Technical Stack

> Last Updated: 2025-09-29
> Version: 1.0.0

## Core Technologies

### Application Framework
- **Framework:** Multi-language support (Python, Node.js, Bash)
- **Primary Language:** Bash scripting for automation
- **Secondary Language:** Python 3.x with UV package management
- **Tertiary Language:** Node.js for JavaScript tooling

### Environment Management
- **Package Manager:** UV (Python)
- **Node Package Manager:** npm
- **Version Control:** Git
- **Environment Isolation:** UV virtual environments per repository

## Repository Management

### Version Control System
- **Primary VCS:** Git
- **Repository Count:** 26+ independent repositories
- **Branch Strategy:** Independent per repository
- **Remote Hosting:** GitHub

### Git Tools
- **Synchronization:** Custom bash scripts
- **Batch Operations:** Multi-repository command execution
- **Status Monitoring:** Automated health checks
- **Conflict Detection:** Pre-sync validation

## Module Architecture

### Module Structure
```
modules/
├── git-management/     # Git operations and synchronization
├── documentation/      # Project documentation and guides
├── config/            # Configuration files and settings
├── automation/        # Automation scripts and tools
├── ci-cd/            # CI/CD pipelines and deployment
├── development/      # Development tools and hooks
├── monitoring/       # Monitoring and reporting tools
└── utilities/        # Utility scripts and helpers
```

### Configuration Management
- **TypeScript Config:** Centralized tsconfig.json
- **Testing Config:** Shared test configurations
- **MCP Settings:** Claude Flow MCP integration
- **Git Hooks:** Standardized validation and auto-formatting

## AI & Orchestration

### AI Integration
- **Platform:** Claude Flow MCP
- **Methodology:** SPARC (Specification, Pseudocode, Architecture, Refinement, Completion)
- **Agent Framework:** Claude Code with 54+ specialized agents
- **Coordination:** Swarm-based task orchestration

### Agent Categories
- **Core Development:** coder, reviewer, tester, planner, researcher
- **Swarm Coordination:** hierarchical-coordinator, mesh-coordinator, adaptive-coordinator
- **Consensus & Distributed:** byzantine-coordinator, raft-manager, gossip-coordinator
- **Performance:** perf-analyzer, performance-benchmarker, task-orchestrator
- **GitHub Integration:** pr-manager, code-review-swarm, issue-tracker
- **SPARC Methodology:** sparc-coord, specification, pseudocode, architecture, refinement

### MCP Tools
- **Coordination:** swarm_init, agent_spawn, task_orchestrate
- **Monitoring:** swarm_status, agent_metrics, task_results
- **Memory & Neural:** memory_usage, neural_train, neural_patterns
- **GitHub:** github_swarm, repo_analyze, pr_enhance, code_review

## Development Tools

### Git Hooks
- **Pre-commit:** Validation and formatting checks
- **Post-edit:** Memory persistence and notification
- **Session Management:** Context restore and metrics export

### Testing Framework
- **Test Runners:** Multiple framework support
- **Coverage Reporting:** Automated coverage generation
- **Integration Tests:** Cross-repository test coordination

### Code Quality
- **Linting:** Configurable per language
- **Type Checking:** TypeScript support
- **Auto-formatting:** Pre-commit hook integration

## CI/CD Infrastructure

### Supported Platforms
- **GitHub Actions:** Primary CI/CD platform
- **Jenkins:** Enterprise integration support
- **CircleCI:** Alternative CI support
- **Azure Pipelines:** Microsoft ecosystem integration

### Deployment Strategy
- **Pipeline Templates:** Reusable workflow configurations
- **Automated Testing:** CI-triggered test execution
- **Status Reporting:** Build and deployment monitoring

## Monitoring & Reporting

### Health Monitoring
- **Repository Status:** Real-time git status aggregation
- **Build Health:** CI/CD pipeline status tracking
- **Dependency Tracking:** UV environment health checks

### Reporting Tools
- **Status Dashboards:** Visual repository health overview
- **Performance Metrics:** Execution time and resource usage
- **Error Tracking:** Aggregated error and warning logs

## Asset Management

### Documentation
- **Format:** Markdown
- **Storage:** Centralized in modules/documentation/
- **Automation:** Auto-generated from code and specs

### Scripts & Tools
- **Language:** Primarily Bash with Python utilities
- **Distribution:** Command propagation system
- **Versioning:** Git-tracked with change history

## Infrastructure

### Development Environment
- **OS Support:** Linux, macOS
- **Shell:** Bash 4.0+
- **Python:** 3.8+ with UV
- **Node:** 18+ LTS

### Repository Hosting
- **Platform:** GitHub
- **Access Control:** Per-repository permissions
- **Backup Strategy:** Git-based with remote mirrors

## Security

### Access Management
- **Authentication:** SSH keys for Git operations
- **Authorization:** Repository-level permissions
- **Secrets Management:** Environment variable based

### Code Safety
- **Pre-commit Validation:** Automated safety checks
- **Dependency Scanning:** UV-based vulnerability checks
- **Git Hooks:** Command validation and sanitization

## Configuration Files

### Key Configuration Files
- `package.json` - Node.js dependencies and scripts
- `pyproject.toml` - Python project configuration (per repository)
- `uv.lock` - UV dependency lock files
- `tsconfig.json` - TypeScript configuration
- `.gitignore` - Git ignore patterns
- `CLAUDE.md` - AI agent configuration

## Dependencies

### Core Dependencies
- **Git:** 2.30+
- **Bash:** 4.0+
- **Python:** 3.8+ with UV
- **Node.js:** 18+ LTS
- **npm:** 9+

### Optional Dependencies
- **Claude Flow:** AI orchestration (@alpha)
- **Ruv-Swarm:** Enhanced coordination (optional)
- **Flow-Nexus:** Cloud features (optional, requires registration)