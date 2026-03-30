---
name: uv-package-manager-1-version-pinning
description: 'Sub-skill of uv-package-manager: 1. Version Pinning (+4).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. Version Pinning (+4)

## 1. Version Pinning


```bash
# Always pin Python version for reproducibility
uv python pin 3.11

# Use version ranges in pyproject.toml
# [project]
# requires-python = ">=3.10,<3.13"
```


## 2. Lock File Hygiene


```bash
# Commit uv.lock to version control
git add uv.lock

# Update regularly
uv lock --upgrade

# Review changes before committing
git diff uv.lock
```


## 3. Dependency Groups


```toml
# pyproject.toml - organize dependencies logically
[project]
dependencies = [
    "pandas>=2.0",
    "numpy>=1.24",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.1.0",
]
viz = [
    "plotly>=5.0",
    "matplotlib>=3.7",
]
ml = [
    "scikit-learn>=1.3",
    "tensorflow>=2.15",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.0",
    "ruff>=0.1.0",
]
```


## 4. Scripts Configuration


```toml
# pyproject.toml - define project scripts
[project.scripts]
my-cli = "my_project.cli:main"

[tool.uv.scripts]
test = "pytest tests/ -v"
lint = "ruff check src/"
format = "black src/ tests/"
typecheck = "mypy src/"
all = ["lint", "typecheck", "test"]
```


## 5. Performance Tips


```bash
# Use parallel installation (default)
uv sync

# Cache packages globally
export UV_CACHE_DIR="$HOME/.cache/uv"

# Offline mode (use cached packages)
uv sync --offline

# Minimal install (no extras)
uv sync --no-dev --no-extras
```
