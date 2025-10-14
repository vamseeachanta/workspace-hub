# Environment Module Documentation

This module contains documentation for Python environment management, UV modernization, and dependency management strategies.

## Overview

The environment module focuses on standardizing Python environment management across all repositories using UV (the modern, fast Python package manager) and ensuring reproducible development environments.

## Documents

### Core Documentation
- **[uv-modernization-plan.md](uv-modernization-plan.md)** - Comprehensive UV modernization plan
- **[uv-modernization-strategy.md](uv-modernization-strategy.md)** - Strategic approach to UV adoption
- **[uv-modernization-summary.md](uv-modernization-summary.md)** - Implementation summary and status

### Analysis
- **[uv-environment-detailed.md](uv-environment-detailed.md)** - Detailed environment analysis
- **[uv-environment-analysis.csv](uv-environment-analysis.csv)** - Quantitative environment data

### Templates
- **[uv-templates/](uv-templates/)** - UV configuration templates and migration tools
  - `pyproject.toml` - Modern Python project configuration
  - `uv.toml` - UV-specific configuration
  - `migrate-to-uv.py` - Automated migration script
  - `validation-checklist.md` - Post-migration validation

## Why UV?

### Performance Benefits
- **10-100x faster** than pip for dependency resolution
- **Instant** virtual environment creation
- **Parallel** package downloads
- **Rust-based** implementation for maximum speed

### Reproducibility
- Built-in lock file management (`uv.lock`)
- Deterministic dependency resolution
- Cross-platform compatibility
- Python version management

### Developer Experience
- Simple CLI (`uv sync`, `uv run`, `uv add`)
- Compatible with existing `pyproject.toml`
- Automatic virtual environment handling
- Clear error messages

## Quick Start

### Install UV
```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Initialize New Project
```bash
uv init my-project
cd my-project
uv add requests pandas numpy
uv sync
```

### Migrate Existing Project
```bash
# Automatic migration
uv init --app

# Manual migration
cp requirements.txt requirements.txt.backup
uv pip compile requirements.txt -o requirements.txt
uv sync
```

### Daily Workflow
```bash
# Install dependencies
uv sync

# Add new dependency
uv add package-name

# Run Python
uv run python script.py

# Run tests
uv run pytest

# Update dependencies
uv lock --upgrade
```

## Migration Strategy

### Phase 1: Pilot Repositories (2 repos)
- ✅ workspace-hub
- ✅ assetutilities

### Phase 2: Python Repositories (5 repos)
- digitalmodel
- pyproject-starter
- achantas-data
- worldenergydata
- Other Python-focused repos

### Phase 3: Remaining Repositories (19 repos)
- All other repositories with Python dependencies

## Configuration Templates

### Standard pyproject.toml
```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.8"
dependencies = [
    "requests>=2.31.0",
    "pandas>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### UV Configuration (uv.toml)
```toml
[project]
managed = true

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "ruff>=0.1.0",
]

[tool.uv.sources]
# Custom package sources if needed
```

## Validation Checklist

After migrating to UV, verify:
- ✅ `uv sync` completes successfully
- ✅ All tests pass with `uv run pytest`
- ✅ Development tools work (`uv run ruff check`)
- ✅ CI/CD updated to use UV
- ✅ Documentation updated
- ✅ Team trained on UV commands

## Troubleshooting

### Common Issues

**Issue**: Dependencies not resolving
```bash
# Solution: Clear cache and retry
uv cache clean
uv sync --refresh
```

**Issue**: Python version mismatch
```bash
# Solution: Specify Python version
uv python install 3.11
uv sync --python 3.11
```

**Issue**: Conflicts with existing venv
```bash
# Solution: Remove old venv and recreate
rm -rf venv/
uv sync
```

## Related Documentation
- [CI/CD Integration](../ci-cd/ci-cd-baseline-integration.md)
- [Testing Standards](../testing/baseline-testing-standards.md)
- [UV Templates](uv-templates/)
- [Migration Script](uv-templates/migrate-to-uv.py)

---
*Part of the workspace-hub environment standardization initiative*
