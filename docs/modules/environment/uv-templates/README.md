# UV Templates and Configuration Files

This directory contains comprehensive templates and configuration files for modernizing Python projects with UV (Astral's next-generation Python package manager).

## 📁 Template Files

### Core Configuration Templates

| File | Purpose | Use Case |
|------|---------|----------|
| `uv.toml` | Complete UV configuration template | New projects starting with UV |
| `pyproject.toml` | Modern Python packaging with UV support | Most Python projects |
| `.python-version` | Python version specification | All UV projects |
| `workspace-uv.toml` | Mono-repository workspace configuration | Multi-package repositories |

### Automation and CI/CD

| File | Purpose | Use Case |
|------|---------|----------|
| `migration-script.py` | Automated migration from pip to UV | Existing pip-based projects |
| `ci-cd-templates.yml` | CI/CD configurations for multiple platforms | Production deployments |

## 🚀 Quick Start

### 1. New Project with UV

```bash
# Copy base template
cp uv-templates/pyproject.toml ./pyproject.toml
cp uv-templates/.python-version ./.python-version

# Customize for your project
# Edit pyproject.toml: name, dependencies, etc.

# Initialize UV
uv sync
```

### 2. Migrate Existing Project

```bash
# Automated migration
python uv-templates/migration-script.py .

# Or manual migration
cp uv-templates/pyproject.toml ./pyproject.toml
# Edit and customize
uv add --requirements requirements.txt
uv sync
```

### 3. Mono-repository Setup

```bash
# Copy workspace template
cp uv-templates/workspace-uv.toml ./uv.toml

# Customize workspace members
# Edit uv.toml: add your packages/services

# Initialize workspace
uv sync
```

## 📋 Template Usage Guide

### pyproject.toml Template

**Features:**
- ✅ Modern Python packaging (PEP 517/518/621)
- ✅ UV-specific configuration
- ✅ Development dependency management
- ✅ Tool configurations (ruff, mypy, pytest)
- ✅ Build system setup
- ✅ Optional dependencies for different use cases

**Customization Steps:**
1. Replace `your-project-name` with actual project name
2. Update `description`, `authors`, and URLs
3. Configure dependencies based on your needs
4. Adjust Python version requirements
5. Enable/disable optional dependency groups

### uv.toml Template

**Features:**
- 🔧 Complete UV configuration
- 📦 Dependency group management
- 🛠️ Tool integrations
- 🌍 Workspace support
- ⚡ Performance optimizations

**When to Use:**
- New projects starting fresh with UV
- Projects needing advanced UV features
- Workspace/mono-repo configurations

### Migration Script

**Features:**
- 🔄 Automated pip → UV migration
- 💾 Backup creation
- 🔍 Dry-run mode for testing
- 📊 Project analysis
- ✅ Validation and verification

**Usage:**
```bash
# Preview migration (recommended first)
python migration-script.py --dry-run ./my-project

# Full migration with backup
python migration-script.py --backup ./my-project

# Migration without backup
python migration-script.py --no-backup ./my-project
```

### CI/CD Templates

**Supported Platforms:**
- 🐙 GitHub Actions
- 🦊 GitLab CI
- 🔷 Azure DevOps
- 🐳 Docker
- 🛠️ Makefile/Justfile

**Features:**
- Multi-Python version testing
- Security scanning
- Automated publishing
- Coverage reporting
- Caching optimization

## 🎯 Common Use Cases

### 1. Web Application (FastAPI/Flask)

```bash
# Use pyproject.toml template
cp uv-templates/pyproject.toml ./

# Uncomment web framework dependencies
# Enable 'web' optional dependencies
uv add fastapi uvicorn
uv sync --extra web
```

### 2. Data Science Project

```bash
# Use pyproject.toml template
cp uv-templates/pyproject.toml ./

# Enable data science dependencies
uv add pandas numpy matplotlib jupyter
uv sync --extra data
```

### 3. CLI Application

```bash
# Use pyproject.toml template
cp uv-templates/pyproject.toml ./

# Enable CLI dependencies
uv add click rich
uv sync --extra cli

# Configure entry points in pyproject.toml
```

### 4. Library Package

```bash
# Use pyproject.toml template with minimal dependencies
cp uv-templates/pyproject.toml ./

# Focus on core dependencies only
# Enable build tools for packaging
uv sync --extra build
```

## 🔧 Configuration Options

### UV Tool Configuration

```toml
[tool.uv]
# Core settings
dev-dependencies = ["pytest", "ruff", "mypy"]
index-url = "https://pypi.org/simple"
resolution = "highest"
prerelease = "disallow"

# Performance
cache-dir = ".uv-cache"
compile-bytecode = true

# Environment
virtual-env = ".venv"
```

### Dependency Management

```toml
[project]
dependencies = [
    "requests>=2.31.0",    # Production runtime
]

[project.optional-dependencies]
dev = ["pytest>=7.4.0"]    # Development tools
test = ["pytest-cov"]      # Testing specific
docs = ["sphinx"]          # Documentation
lint = ["ruff", "mypy"]    # Linting tools
```

### Workspace Configuration

```toml
[workspace]
members = ["packages/*", "services/*"]
exclude = ["legacy/*"]

[workspace.dependencies]
shared-lib = ">=1.0.0"    # Shared across workspace
```

## 🚨 Migration Checklist

### Pre-Migration
- [ ] Backup current configuration files
- [ ] Document current environment issues
- [ ] List all installed packages
- [ ] Note custom package sources

### During Migration
- [ ] Run migration script in dry-run mode
- [ ] Review generated pyproject.toml
- [ ] Test dependency resolution
- [ ] Validate environment creation

### Post-Migration
- [ ] Run existing tests
- [ ] Update CI/CD pipelines
- [ ] Update documentation
- [ ] Train team on UV workflows
- [ ] Clean up old configuration files

## 🔍 Troubleshooting

### Common Issues

**1. Package Not Found**
```bash
# Add custom index
uv add package-name --index-url https://custom-index.com/simple
```

**2. Version Conflicts**
```bash
# Override resolution strategy
[tool.uv]
resolution = "lowest-direct"
```

**3. Platform-Specific Dependencies**
```toml
dependencies = [
    "pywin32>=306; sys_platform == 'win32'",
    "uvloop>=0.19.0; sys_platform != 'win32'",
]
```

### Validation Commands

```bash
# Check configuration
uv check

# Validate dependencies
uv tree

# Test environment
uv run python -c "import sys; print(sys.path)"

# Run tests
uv run pytest
```

## 📚 Additional Resources

### Documentation
- [UV Official Documentation](https://docs.astral.sh/uv/)
- [Python Packaging Guide](https://packaging.python.org/)
- [PyProject.toml Specification](https://peps.python.org/pep-0621/)

### Migration Guides
- [From pip to UV](../uv-modernization-strategy.md)
- [From Poetry to UV](https://docs.astral.sh/uv/guides/integration/poetry/)
- [From Pipenv to UV](https://docs.astral.sh/uv/guides/integration/pipenv/)

### Best Practices
- [UV Best Practices](https://docs.astral.sh/uv/guides/best-practices/)
- [Python Project Structure](https://docs.python-guide.org/writing/structure/)
- [Testing with pytest](https://docs.pytest.org/)

## 🤝 Contributing

To improve these templates:

1. Test with various project types
2. Update for new UV features
3. Add platform-specific configurations
4. Include more CI/CD platforms
5. Enhance migration script capabilities

## 📄 License

These templates are provided under the MIT License. Customize and use them freely in your projects.

---

*These templates are maintained as part of the UV modernization strategy. For questions or improvements, please refer to the main strategy document.*