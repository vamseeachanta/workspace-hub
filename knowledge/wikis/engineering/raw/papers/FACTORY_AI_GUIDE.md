# Factory.ai Integration Guide

> **Workspace Hub** - Multi-Repository Development with AI Droids
>
> Factory.ai Version: v0.18.0
> Last Updated: 2025-10-03

## Overview

Factory.ai provides AI-powered development agents (Droids) that automate coding tasks across your entire workspace. This guide covers installation, configuration, and usage across all 26 repositories in workspace-hub.

## 🚀 What is Factory.ai?

Factory.ai is an **Agent-Native Software Development** platform that provides intelligent coding agents called **Droids**. These agents can:

- Automate complete tasks (refactors, migrations, features)
- Work across multiple environments (IDE, terminal, browser)
- Delegate coding work as you think of it
- Integrate seamlessly with existing workflows

## ✅ Installation Status

Factory.ai is **fully installed** across workspace-hub:

### CLI Installation
- **Location:** `/home/vamsee/.local/bin/droid`
- **Version:** v0.18.0
- **Command:** `droid` (globally available)

### Repository Coverage

All 26 repositories are initialized with factory.ai:

**Workspace Hub Root:**
- `.drcode/config.json` - Master configuration

**Sub-Repositories (25):**
- aceengineer-admin
- aceengineercode
- aceengineer-website
- achantas-data
- achantas-media
- acma-projects
- ai-native-traditional-eng
- assethold
- assetutilities
- client_projects
- digitalmodel
- doris
- energy
- frontierdeepwater
- hobbies
- investments
- OGManufacturing
- pyproject-starter
- rock-oil-field
- sabithaandkrishnaestates
- saipem
- sd-work
- seanation
- teamresumes
- worldenergydata

Each repository has its own `.drcode/config.json` that references the workspace-hub parent configuration.

## 📖 Basic Usage

### Interactive Mode

Start an interactive session with a Droid in any repository:

```bash
cd /path/to/repository
droid
```

The Droid will:
1. Open a browser for authentication (first time only)
2. Start an interactive chat session
3. Execute tasks you describe in natural language

### Non-Interactive Mode

Execute tasks directly from command line (great for automation):

```bash
# Single command execution
droid exec "add type hints to all Python functions"

# From stdin (for scripts)
echo "refactor this code to use async/await" | droid exec -

# With file input
droid exec - < task-description.txt
```

### Command Options

```bash
droid --version        # Show version
droid --help          # Show help
droid exec --help     # Show exec command options
```

## 🎯 Common Use Cases

### 1. Code Refactoring

```bash
cd your-repository
droid exec "refactor all classes to use dependency injection"
```

### 2. Feature Implementation

```bash
droid exec "add user authentication with JWT tokens"
```

### 3. Bug Fixes

```bash
droid exec "fix the memory leak in the data processing module"
```

### 4. Testing

```bash
droid exec "write unit tests for all API endpoints with 90% coverage"
```

### 5. Documentation

```bash
droid exec "generate API documentation from code comments"
```

### 6. Code Migration

```bash
droid exec "migrate from Python 3.8 to Python 3.11 syntax"
```

### 7. Performance Optimization

```bash
droid exec "optimize database queries in the user service"
```

## 🔧 Configuration

### Workspace-Level Configuration

**Location:** `/mnt/github/workspace-hub/.drcode/config.json`

```json
{
  "version": "1.0",
  "workspace": "workspace-hub",
  "description": "Multi-repository workspace with centralized management",
  "features": {
    "multiRepo": true,
    "automation": true,
    "cicd": true
  }
}
```

### Repository-Level Configuration

Each repository has its own config at `<repo>/.drcode/config.json`:

```json
{
  "version": "1.0",
  "repository": "repo-name",
  "workspace": "workspace-hub",
  "parentConfig": "../../.drcode/config.json"
}
```

## 🔄 Re-initialization Script

If you need to reinitialize factory.ai across all repositories:

```bash
/mnt/github/workspace-hub/modules/automation/install_factory_all_repos.sh
```

This script will:
- ✓ Verify droid CLI installation
- ✓ Initialize workspace-hub root
- ✓ Initialize all 25 sub-repositories
- ✓ Create or update `.drcode/config.json` files
- ✓ Provide summary of actions taken

## 🔐 Authentication

On first use, factory.ai will:
1. Open your default browser
2. Prompt you to sign in
3. Store credentials locally
4. No further authentication needed

## 📊 Integration with Workspace Hub

### Module Organization

Factory.ai integrates with workspace-hub's modular structure:

```
workspace-hub/
├── .drcode/                    # Factory.ai workspace config
├── modules/
│   ├── automation/
│   │   └── install_factory_all_repos.sh
│   ├── git-management/
│   ├── ci-cd/
│   └── ...
└── [25 repositories]/
    └── .drcode/               # Per-repo factory.ai config
```

### Workflow Integration

Factory.ai Droids work alongside:
- **Claude Flow:** AI orchestration and coordination
- **SPARC Methodology:** Systematic development phases
- **Git Management:** Multi-repository operations
- **CI/CD Pipelines:** Automated testing and deployment

## 💡 Best Practices

### 1. Be Specific in Task Descriptions

❌ Bad: "fix the code"
✅ Good: "fix the SQL injection vulnerability in user_controller.py line 45"

### 2. Start Small

Begin with smaller, well-defined tasks to understand how Droids work before tackling complex refactors.

### 3. Review Changes

Always review code changes before committing. Droids are powerful but should be supervised.

### 4. Use Interactive Mode for Complex Tasks

For multi-step or ambiguous tasks, interactive mode allows you to guide the Droid.

### 5. Combine with Version Control

Work on feature branches when using Droids to easily review and rollback if needed.

### 6. Save Successful Commands

Document successful droid commands in your team wiki for reuse.

## 🔍 Troubleshooting

### Command Not Found

```bash
# Check installation
which droid

# Should output: /home/vamsee/.local/bin/droid
# If not found, ensure ~/.local/bin is in PATH
```

### Authentication Issues

```bash
# Clear credentials and re-authenticate
rm -rf ~/.factory
droid
```

### Repository Not Initialized

```bash
# Reinitialize specific repository
cd repository-name
mkdir -p .drcode
cat > .drcode/config.json << EOF
{
  "version": "1.0",
  "repository": "$(basename $(pwd))",
  "workspace": "workspace-hub",
  "parentConfig": "../../.drcode/config.json"
}
EOF
```

### Droid Not Responding

1. Check internet connection
2. Verify factory.ai service status at https://factory.ai/status
3. Try non-interactive mode: `droid exec "test"`
4. Check logs: `~/.factory/logs/`

## 📚 Additional Resources

### Official Documentation
- **Main Docs:** https://docs.factory.ai
- **CLI Guide:** https://docs.factory.ai/cli/getting-started/overview
- **Quickstart:** https://docs.factory.ai/cli/getting-started/quickstart

### Workspace Hub Integration
- **AI Ecosystem:** `docs/AI_ECOSYSTEM.md`
- **Automation Scripts:** `modules/automation/`
- **CLAUDE.md:** Root configuration for AI agents

### Support
- **Factory.ai Support:** https://factory.ai/support
- **GitHub Issues:** Report workspace-specific issues in this repository

## 🎓 Examples

### Example 1: Add Logging

```bash
cd myproject
droid exec "add comprehensive logging to all functions using Python's logging module"
```

### Example 2: Database Migration

```bash
cd backend
droid exec "create Alembic migration to add 'last_login' column to users table"
```

### Example 3: API Endpoint

```bash
cd api-service
droid exec "create RESTful endpoint for user profile with GET, PUT, DELETE methods"
```

### Example 4: Test Suite

```bash
cd application
droid exec "create pytest test suite for calculator.py with edge cases"
```

### Example 5: Security Audit

```bash
droid exec "audit authentication.py for security vulnerabilities and fix them"
```

## 🔄 Workflow Example

Complete feature development with factory.ai:

```bash
# 1. Create feature branch
git checkout -b feature/user-notifications

# 2. Implement feature
droid exec "implement user notification system with email and SMS support"

# 3. Add tests
droid exec "write unit and integration tests for notification system"

# 4. Generate docs
droid exec "create API documentation for notification endpoints"

# 5. Review and commit
git add .
git commit -m "Add user notification system"

# 6. Push and create PR
git push origin feature/user-notifications
```

## ⚙️ Advanced Usage

### Scripting with Droid

```bash
#!/bin/bash
# automated-refactor.sh

REPOS=(
  "aceengineercode"
  "pyproject-starter"
  "client_projects"
)

for repo in "${REPOS[@]}"; do
  echo "Processing $repo..."
  cd "/mnt/github/workspace-hub/$repo"
  droid exec "refactor to use async/await pattern" || echo "Failed: $repo"
done
```

### Task Chaining

```bash
# Chain multiple tasks
droid exec "add type hints" && \
droid exec "run mypy and fix errors" && \
droid exec "update tests for new types"
```

### Environment-Specific Tasks

```bash
# Development environment
export ENV=dev
droid exec "configure development database connection"

# Production environment
export ENV=prod
droid exec "configure production database connection with SSL"
```

## 📈 Next Steps

1. **Explore Interactive Mode:** Run `droid` in a test repository
2. **Try Simple Tasks:** Start with documentation or testing tasks
3. **Integrate with Workflow:** Add droid commands to your development scripts
4. **Share Success Stories:** Document successful automations for team reuse
5. **Combine with Claude Flow:** Use both for maximum automation

---

**Factory.ai is now ready to accelerate development across all 26 workspace-hub repositories!**

For questions or issues, refer to the troubleshooting section or official documentation.
