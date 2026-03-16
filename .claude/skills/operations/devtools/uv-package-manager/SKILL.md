---
name: ops-uv-package-manager
version: 1.0.0
description: UV for fast Python package management, virtual environments, and project
  workflows
author: workspace-hub
category: operations
tags:
- uv
- python
- package-manager
- virtual-environment
- dependency-management
platforms:
- python
- linux
- macos
- windows
capabilities: []
requires: []
see_also:
- ops-uv-package-manager-1-project-initialization
- ops-uv-package-manager-5-running-scripts-and-commands
- ops-uv-package-manager-1-version-pinning
---

# Ops Uv Package Manager

## When to Use This Skill

Use UV package manager when you need:
- **Fast dependency installation** - 10-100x faster than pip
- **Virtual environment management** - Create and manage venvs effortlessly
- **Project initialization** - Start new Python projects quickly
- **Dependency resolution** - Reliable, reproducible dependency trees
- **Lock file management** - Ensure consistent environments across machines
- **Python version management** - Install and switch Python versions

**Avoid when:**
- Legacy systems requiring pip compatibility (rare)
- Conda-based scientific computing environments
- Docker images with pre-installed pip workflows

## Installation

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Homebrew
brew install uv

# pip (if needed)
pip install uv
```

## Complete Examples

### Example 1: New Project Setup

```bash
#!/bin/bash
# setup_project.sh - Initialize a new Python project with UV

PROJECT_NAME=${1:-"my-project"}

# Create and enter project
uv init "$PROJECT_NAME"
cd "$PROJECT_NAME"


*See sub-skills for full details.*
### Example 2: Migrate from pip to UV

```bash
#!/bin/bash
# migrate_to_uv.sh - Migrate existing project to UV

# Backup existing requirements
cp requirements.txt requirements.txt.bak 2>/dev/null || true

# Initialize UV project (if pyproject.toml doesn't exist)
if [ ! -f pyproject.toml ]; then
    uv init --no-readme

*See sub-skills for full details.*
### Example 3: CI/CD Pipeline with UV

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]


*See sub-skills for full details.*
### Example 4: Multi-Environment Management

```bash
#!/bin/bash
# manage_envs.sh - Manage multiple Python environments

# Function to create environment for specific Python version
create_env() {
    local py_version=$1
    local env_name=".venv-py${py_version//./}"

    echo "Creating environment for Python $py_version..."

*See sub-skills for full details.*
### Example 5: Workspace-Hub Project Setup

```bash
#!/bin/bash
# setup_workspace_project.sh - Setup project following workspace-hub patterns

PROJECT_NAME=${1:-"new-project"}
TEMPLATE_REPO="workspace-hub/pyproject-starter"

# Initialize with UV
uv init "$PROJECT_NAME"
cd "$PROJECT_NAME"

*See sub-skills for full details.*

## Development Commands

```bash
# Install dependencies
uv sync --dev

# Run tests
uv run pytest tests/ -v

# Run linting
uv run ruff check src/

# Run formatting
uv run black src/ tests/
uv run isort src/ tests/

# Run type checking
uv run mypy src/
```

## Project Structure

- `src/` - Source code
- `tests/` - Test files
- `docs/` - Documentation
- `data/` - Data files (raw, processed, results)
- `reports/` - Generated HTML reports
- `config/` - Configuration files
EOF

echo "Project $PROJECT_NAME created with workspace-hub patterns!"
```

## Common Commands Reference

| Command | Description |
|---------|-------------|
| `uv init` | Initialize new project |
| `uv venv` | Create virtual environment |
| `uv add <pkg>` | Add dependency |
| `uv add --dev <pkg>` | Add dev dependency |
| `uv remove <pkg>` | Remove dependency |
| `uv sync` | Install all dependencies |
| `uv lock` | Update lock file |
| `uv run <cmd>` | Run command in venv |
| `uv python list` | List Python versions |
| `uv python install` | Install Python version |
| `uv pip install` | pip compatibility mode |
| `uv build` | Build package |
| `uv publish` | Publish to PyPI |

## Resources

- **UV Documentation**: https://docs.astral.sh/uv/
- **UV GitHub**: https://github.com/astral-sh/uv
- **Migration Guide**: https://docs.astral.sh/uv/guides/migration/
- **pyproject.toml Spec**: https://packaging.python.org/en/latest/specifications/pyproject-toml/

---

**Use UV for all Python projects in workspace-hub!**

## Sub-Skills

- [1. Project Initialization (+3)](1-project-initialization/SKILL.md)
- [5. Running Scripts and Commands (+1)](5-running-scripts-and-commands/SKILL.md)
- [1. Version Pinning (+4)](1-version-pinning/SKILL.md)
