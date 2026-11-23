# UV Environment Modernization Plan

**Date:** 2025-09-28
**Status:** Ready for Implementation
**Scope:** All 27 Repositories

## Executive Summary

This document outlines a comprehensive modernization plan for UV package management across all repositories. Currently, 88.5% of repositories have UV configured, but many are using outdated configurations and dependencies that need modernization.

## Current State Analysis

### UV Adoption Status
- **23 repositories (88.5%)** - Already have UV configured
- **3 repositories (11.5%)** - Need UV migration from pip/Poetry
- **1 repository** - Uses Poetry but has UV config (assethold)

### Repositories Requiring Migration

#### High Priority (Complex Dependencies)
1. **assethold** - Uses Poetry, has 60+ dependencies, needs full migration
2. **assetutilities** - Complex pip dependencies, no UV config

#### Medium Priority (Simple Migration)
3. **investments** - Clean pyproject.toml, just needs UV config
4. **achantas-data** - Basic pip setup, straightforward migration

### Critical Modernization Needs

#### aceengineercode (URGENT - Security Risk)
- **pandas 0.23.0** (2018 release) → Upgrade to 2.1.4+
- **PyYAML** outdated → Security vulnerabilities
- **Flask** outdated → Multiple CVEs fixed in newer versions
- Python constraint `>=3.8` → Update to `>=3.9`

## Modernization Strategy

### Phase 1: Critical Security Updates (Week 1)
Focus on repositories with known vulnerabilities and outdated dependencies.

**Target Repositories:**
- aceengineercode (critical security updates)
- aceengineer-website (Flask updates)
- All repositories with PyYAML < 6.0.1

### Phase 2: UV Migration (Week 2)
Migrate repositories still using pip/Poetry to UV.

**Migration Order:**
1. investments (simple, clean structure)
2. achantas-data (basic dependencies)
3. assetutilities (complex but manageable)
4. assethold (most complex, Poetry migration)

### Phase 3: Configuration Standardization (Week 3)
Update all UV configurations to modern standards.

**Standards to Apply:**
- Minimum Python 3.9 (EOL for 3.8 is Oct 2024)
- UV workspace configurations for related repos
- Separate dev/test/doc dependency groups
- Lock file generation and caching
- Script definitions in pyproject.toml

### Phase 4: Advanced Features (Week 4)
Implement UV's advanced features for improved DX.

**Features to Add:**
- UV workspaces for multi-package repos
- Custom scripts in pyproject.toml
- Tool configurations (ruff, mypy, pytest)
- Pre-commit hooks with UV
- GitHub Actions optimization with UV cache

## Repository-Specific Modernization Plans

### 1. investments (pip → UV)

**Current:** Basic pip with clean pyproject.toml
**Migration Steps:**
```bash
# Install UV and initialize
uv init --no-workspace
uv add pyyaml>=6.0.1
uv add --dev pytest>=7.0 pytest-cov>=4.0 black>=23.0 isort>=5.12 flake8>=6.0 mypy>=1.0
uv lock
```

**New uv.toml:**
```toml
[project]
name = "investments"
version = "0.1.0"
requires-python = ">=3.9"

[tool.uv]
dev-dependencies = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "black>=24.0",
    "ruff>=0.5",
    "mypy>=1.10",
]

[tool.uv.sources]
assetutilities = { path = "../assetutilities" }  # If local dependency
```

### 2. achantas-data (pip → UV)

**Current:** Simple pip setup
**Migration:** Similar to investments, focus on data science packages
```bash
uv init --no-workspace
uv add pandas>=2.0 numpy>=1.24 matplotlib>=3.7
uv add --dev jupyter>=1.0 ipykernel>=6.0
uv lock
```

### 3. assetutilities (pip → UV)

**Current:** Complex dependencies, used by other projects
**Migration Strategy:**
- Create UV workspace configuration
- Define as a library package
- Careful dependency resolution

```toml
# uv.toml
[workspace]
members = [".", "../assethold"]  # If managing together

[project]
name = "assetutilities"
version = "0.2.0"
requires-python = ">=3.9"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### 4. assethold (Poetry → UV)

**Current:** Poetry with 60+ dependencies
**Migration Complexity:** High

**Step-by-step Migration:**
```bash
# Export Poetry dependencies
poetry export -f requirements.txt -o requirements.txt --without-hashes

# Initialize UV
uv init --no-workspace

# Parse and add dependencies
uv pip compile requirements.txt -o requirements.lock
uv add --from requirements.lock

# Add dev dependencies
uv add --dev pytest black ruff mypy

# Clean up
rm poetry.lock pyproject.toml.bak
```

### 5. aceengineercode (Security Updates)

**Critical Updates Required:**
```toml
# Updated dependencies
dependencies = [
    "pandas>=2.1.4",
    "numpy>=1.24.0",
    "PyYAML>=6.0.1",
    "Flask>=3.0.0",
    "matplotlib>=3.7.0",
    "scikit-learn>=1.3.0",
    "requests>=2.31.0",
    "beautifulsoup4>=4.12.0",
]
```

## UV Best Practices

### 1. Python Version Management
```toml
# Recommended minimum
requires-python = ">=3.9"

# Or be more specific for consistency
requires-python = ">=3.9,<3.13"
```

### 2. Dependency Groups
```toml
[project.optional-dependencies]
dev = ["pytest>=8.0", "black>=24.0", "ruff>=0.5"]
test = ["pytest>=8.0", "pytest-cov>=5.0", "pytest-xdist>=3.5"]
docs = ["sphinx>=7.0", "sphinx-rtd-theme>=2.0"]
viz = ["matplotlib>=3.7", "plotly>=5.18", "seaborn>=0.13"]
```

### 3. UV Scripts
```toml
[tool.uv.scripts]
test = "pytest tests/ -v --cov=src"
lint = "ruff check . && black --check ."
format = "ruff check . --fix && black ."
typecheck = "mypy src/"
docs = "sphinx-build docs docs/_build"
```

### 4. Workspace Configuration
For related repositories:
```toml
[workspace]
members = [
    "aceengineer-admin",
    "aceengineercode",
    "aceengineer-website",
]

[workspace.package]
requires-python = ">=3.9"

[workspace.dependencies]
pytest = ">=8.0"
black = ">=24.0"
```

### 5. GitHub Actions with UV
```yaml
- name: Set up UV
  uses: astral-sh/setup-uv@v3
  with:
    version: "0.4.0"
    enable-cache: true
    cache-dependency-glob: "**/pyproject.toml"

- name: Install dependencies
  run: |
    uv sync --all-extras --dev
    uv pip list  # For debugging

- name: Run tests
  run: uv run pytest
```

## Migration Scripts

### Batch UV Initialization Script
```bash
#!/bin/bash
# uv-migrate.sh - Batch UV migration for multiple repos

REPOS=(
    "investments"
    "achantas-data"
    "assetutilities"
)

for repo in "${REPOS[@]}"; do
    echo "Migrating $repo to UV..."
    cd "/mnt/github/github/$repo"

    # Backup existing config
    cp pyproject.toml pyproject.toml.bak 2>/dev/null

    # Initialize UV
    uv init --no-workspace

    # Add Python constraint
    uv python pin ">=3.9"

    # Parse and add existing dependencies
    if [ -f "requirements.txt" ]; then
        uv pip compile requirements.txt -o requirements.lock
        uv add --from requirements.lock
    fi

    # Add standard dev dependencies
    uv add --dev pytest pytest-cov black ruff mypy

    # Generate lock file
    uv lock

    echo "✅ $repo migrated to UV"
done
```

### Poetry to UV Migration Script
```python
#!/usr/bin/env python3
# poetry_to_uv.py - Convert Poetry projects to UV

import tomli
import tomli_w
from pathlib import Path
import subprocess

def migrate_poetry_to_uv(project_path: Path):
    """Migrate a Poetry project to UV."""

    # Read Poetry pyproject.toml
    poetry_toml = project_path / "pyproject.toml"
    with open(poetry_toml, "rb") as f:
        poetry_config = tomli.load(f)

    # Extract dependencies
    deps = poetry_config.get("tool", {}).get("poetry", {}).get("dependencies", {})
    dev_deps = poetry_config.get("tool", {}).get("poetry", {}).get("dev-dependencies", {})

    # Remove Python from deps
    deps.pop("python", None)

    # Initialize UV
    subprocess.run(["uv", "init", "--no-workspace"], cwd=project_path)

    # Add dependencies
    for dep, version in deps.items():
        if dep != "python":
            cmd = ["uv", "add", f"{dep}{version}"] if isinstance(version, str) else ["uv", "add", dep]
            subprocess.run(cmd, cwd=project_path)

    # Add dev dependencies
    for dep, version in dev_deps.items():
        cmd = ["uv", "add", "--dev", f"{dep}{version}"] if isinstance(version, str) else ["uv", "add", "--dev", dep]
        subprocess.run(cmd, cwd=project_path)

    # Generate lock
    subprocess.run(["uv", "lock"], cwd=project_path)

    print(f"✅ Migrated {project_path.name} from Poetry to UV")

if __name__ == "__main__":
    migrate_poetry_to_uv(Path("/mnt/github/github/assethold"))
```

## Performance Benefits

### UV vs Traditional Tools
- **10-100x faster** than pip for dependency resolution
- **2-8x faster** than Poetry for large projects
- **Built-in caching** reduces redundant downloads
- **Parallel downloads** for faster installation
- **Rust-based** for maximum performance

### Expected Improvements
- **Development setup**: From ~2 minutes to ~10 seconds
- **CI/CD pipelines**: 50-70% faster dependency installation
- **Docker builds**: Significantly smaller layers with better caching
- **Developer experience**: Instant feedback on dependency conflicts

## Implementation Timeline

### Week 1: Critical Updates & Security
- Day 1-2: Update aceengineercode dependencies
- Day 3-4: Security patches across all repos
- Day 5: Verification and testing

### Week 2: UV Migrations
- Day 1: Migrate investments and achantas-data
- Day 2-3: Migrate assetutilities
- Day 4-5: Migrate assethold from Poetry

### Week 3: Standardization
- Day 1-2: Update Python constraints to >=3.9
- Day 3-4: Implement dependency groups
- Day 5: Add UV scripts to all repos

### Week 4: Advanced Features
- Day 1-2: Setup UV workspaces
- Day 3-4: Optimize GitHub Actions
- Day 5: Documentation and training

## Success Metrics

### Technical Metrics
- ✅ 100% UV adoption across all repos
- ✅ All dependencies updated to latest stable versions
- ✅ Python >=3.9 minimum across all projects
- ✅ Lock files generated for reproducible builds
- ✅ CI/CD optimized with UV caching

### Security Metrics
- ✅ Zero known vulnerabilities in dependencies
- ✅ All packages updated within last 12 months
- ✅ Automated dependency scanning enabled
- ✅ Security update process documented

### Developer Experience
- ✅ Setup time reduced by 80%+
- ✅ Consistent tooling across all projects
- ✅ Clear documentation and examples
- ✅ Automated migration scripts available

## Risk Mitigation

### Potential Issues & Solutions

1. **Breaking Changes in Dependencies**
   - Solution: Comprehensive test coverage before updates
   - Fallback: Maintain version pins for critical packages

2. **Poetry Migration Complexity**
   - Solution: Automated migration script with validation
   - Fallback: Manual migration with careful testing

3. **CI/CD Disruption**
   - Solution: Gradual rollout with parallel pipelines
   - Fallback: Maintain old pipeline until UV proven stable

4. **Developer Training**
   - Solution: Comprehensive documentation and examples
   - Fallback: Pair programming sessions for complex migrations

## Conclusion

UV modernization will bring significant performance improvements, enhanced security, and better developer experience across all repositories. The phased approach minimizes risk while ensuring comprehensive coverage.

**Next Steps:**
1. Review and approve this plan
2. Begin Phase 1 critical security updates
3. Schedule migration windows for each repository
4. Prepare team training materials
5. Set up monitoring for post-migration metrics

---

*This plan provides a systematic approach to modernizing UV environments while maintaining stability and security across all projects.*