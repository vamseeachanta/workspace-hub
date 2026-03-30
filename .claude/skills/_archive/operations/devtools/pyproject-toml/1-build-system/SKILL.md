---
name: ops-pyproject-toml-1-build-system
description: 'Sub-skill of ops-pyproject-toml: 1. Build System (+4).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. Build System (+4)

## 1. Build System


```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"
```

**Alternative build backends:**
```toml
# Hatch
[build-system]

*See sub-skills for full details.*

## 2. Project Metadata


```toml
[project]
name = "my-project"                    # Package name (PyPI)
version = "0.1.0"                      # Semantic version
description = "Short description"      # One-line summary
readme = "README.md"                   # Long description file
requires-python = ">=3.10"             # Python version constraint
license = {text = "MIT"}               # License identifier

# Alternative license formats

*See sub-skills for full details.*

## 3. Dependencies


```toml
[project]
# Core dependencies (always installed)
dependencies = [
    "pandas>=2.0.0",           # Minimum version
    "numpy>=1.24,<2.0",        # Version range
    "requests~=2.28",          # Compatible release
    "click==8.1.3",            # Exact version
    "pyyaml",                  # Any version
]

*See sub-skills for full details.*

## 4. Package Discovery


**Src layout (recommended):**
```toml
[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
include = ["my_project*"]
exclude = ["tests*"]
```

*See sub-skills for full details.*

## 5. Entry Points


**CLI scripts:**
```toml
[project.scripts]
# Creates: my-cli command
my-cli = "my_project.cli:main"

# Module with arguments
my-tool = "my_project.tools:run"
```


*See sub-skills for full details.*
