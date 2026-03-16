---
name: ops-uv-package-manager-1-project-initialization
description: 'Sub-skill of ops-uv-package-manager: 1. Project Initialization (+3).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. Project Initialization (+3)

## 1. Project Initialization


**Create a new Python project:**
```bash
# Initialize new project with pyproject.toml
uv init my-project
cd my-project

# Initialize in current directory
uv init

# Initialize with specific Python version
uv init --python 3.11
```

**Project structure created:**
```
my-project/
├── .python-version      # Python version lock
├── pyproject.toml       # Project configuration
├── README.md            # Project readme
└── src/
    └── my_project/
        └── __init__.py
```


## 2. Virtual Environment Management


**Create and activate virtual environments:**
```bash
# Create venv (default .venv directory)
uv venv

# Create with specific Python version
uv venv --python 3.11

# Create with custom name
uv venv .venv-test

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Activate (Git Bash on Windows)
source .venv/Scripts/activate
```

**List available Python versions:**
```bash
# List installed Python versions
uv python list

# Install specific Python version
uv python install 3.12

# Pin Python version for project
uv python pin 3.11
```


## 3. Dependency Management


**Add dependencies:**
```bash
# Add a single package
uv add pandas

# Add multiple packages
uv add numpy scipy matplotlib

# Add with version constraints
uv add "pandas>=2.0,<3.0"

# Add development dependencies
uv add --dev pytest pytest-cov ruff

# Add optional dependencies
uv add --optional ml tensorflow torch

# Add from git repository
uv add git+https://github.com/user/repo.git

# Add local package in editable mode
uv add --editable ../my-local-package
```

**Remove dependencies:**
```bash
# Remove a package
uv remove pandas

# Remove dev dependency
uv remove --dev pytest
```

**Sync dependencies:**
```bash
# Install all dependencies from pyproject.toml
uv sync

# Sync including dev dependencies
uv sync --dev

# Sync with optional dependencies
uv sync --extra ml

# Sync all extras
uv sync --all-extras
```


## 4. Lock File Management


**Understanding uv.lock:**
```bash
# Lock file is auto-generated on uv add/sync
# Contains exact versions for reproducibility

# Regenerate lock file
uv lock

# Lock with specific Python version
uv lock --python 3.11

# Update all dependencies to latest
uv lock --upgrade

# Update specific package
uv lock --upgrade-package pandas
```

**Lock file structure:**
```toml
# uv.lock (auto-generated, do not edit manually)
version = 1
requires-python = ">=3.9"

[[package]]
name = "pandas"
version = "2.2.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "numpy" },
    { name = "python-dateutil" },
    { name = "pytz" },
]
```
