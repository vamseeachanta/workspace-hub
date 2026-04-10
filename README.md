# Repository Management Hub

A centralized management system for multiple GitHub repositories with modular organization.

## 📁 Module Structure

```
modules/
├── git-management/     # Git operations and synchronization tools
├── documentation/      # Project documentation and guides
├── config/            # Configuration files and settings
├── automation/        # Automation scripts and tools
├── ci-cd/            # CI/CD pipelines and deployment
├── development/      # Development tools and hooks
├── monitoring/       # Monitoring and reporting tools
└── utilities/        # Utility scripts and helpers
```

## 🚀 Quick Start

### Repository Status Check
```bash
./modules/git-management/check_all_repos_status.sh
```

### Pull All Repositories
```bash
./modules/git-management/pull_all_repos.sh
```

### Sync All Repositories
```bash
./modules/git-management/git_sync_all.sh
```

## 📦 Managed Repositories

This hub manages 25 independent Git repositories while maintaining their autonomy. Each repository:
- Maintains its own Git history
- Has independent remote connections
- Can be managed individually

## 📋 Modules

### Git Management
Tools for managing multiple Git repositories simultaneously.
- Batch operations
- Synchronization
- Branch management
- Status reporting

### Documentation
Comprehensive documentation for all tools and processes.
- Agent setup guides
- Command references
- Best practices
- Architecture documentation

### Configuration
Centralized configuration management.
- Package configurations
- TypeScript settings
- Testing configurations
- MCP settings

### Automation
Scripts for automating repetitive tasks.
- Command propagation
- Spec synchronization
- Resource management

### CI/CD
Continuous Integration and Deployment tools.
- GitHub Actions
- Jenkins
- CircleCI
- Azure Pipelines

### Development
Development environment tools and hooks.
- Git hooks
- Testing utilities
- Code quality tools

### Monitoring
System monitoring and reporting.
- Performance metrics
- Error tracking
- Notification systems

### Utilities
General-purpose utility scripts.
- File operations
- Data processing
- Helper functions

## 🔧 Configuration

See `modules/config/` for all configuration files.

## 📖 Documentation

Detailed documentation available in `modules/documentation/`.

- **[Skills Index](docs/SKILLS_INDEX.md)** - Complete catalog of Claude Code skills across all repositories
- **[Repository Overview](docs/WORKSPACE_HUB_REPOSITORY_OVERVIEW.md)** - Repository relationships & navigation

## AI Review Workflows

This workspace includes automated code review workflows:

- **Gemini Review**: Automatically reviews ALL commits across all repositories using Google Gemini.
  - Documentation: [docs/modules/ai/GEMINI_REVIEW_WORKFLOW.md](docs/modules/ai/GEMINI_REVIEW_WORKFLOW.md)
  - Manager: `./scripts/ai-review/gemini-review-manager.sh list`
- **Codex Review**: Reviews Claude-authored commits using OpenAI Codex.
  - Documentation: [docs/modules/ai/CODEX_REVIEW_WORKFLOW.md](docs/modules/ai/CODEX_REVIEW_WORKFLOW.md)
  - Manager: `./scripts/ai-review/review-manager.sh list`

## Operational Audits

- **Provider Session Ecosystem Audit**: Cross-provider session-log health report for Claude, Codex, Hermes, and Gemini.
  - Report: [docs/reports/provider-session-ecosystem-audit.md](docs/reports/provider-session-ecosystem-audit.md)
  - Run: `uv run --no-project python scripts/analysis/provider_session_ecosystem_audit.py --stdout`
  - Wrapper: `bash scripts/cron/provider-session-ecosystem-audit.sh`

## Setup & Maintenance

## 🤝 Contributing

1. Work within the appropriate module
2. Follow the existing structure
3. Update module README when adding features
4. Test changes before committing

## 📄 License

[Your License Here]

---

*Repository Management Hub - Keeping your projects organized*