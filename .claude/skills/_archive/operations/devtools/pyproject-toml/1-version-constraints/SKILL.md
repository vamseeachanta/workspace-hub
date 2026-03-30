---
name: ops-pyproject-toml-1-version-constraints
description: 'Sub-skill of ops-pyproject-toml: 1. Version Constraints (+3).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. Version Constraints (+3)

## 1. Version Constraints


```toml
# Recommended patterns
dependencies = [
    "pandas>=2.0.0",           # Minimum version (most common)
    "numpy>=1.24,<2.0",        # Range for major version compatibility
    "requests~=2.28",          # Compatible release (~=2.28 means >=2.28,<3.0)
]

# Avoid
dependencies = [
    "pandas==2.1.3",           # Too strict, causes conflicts
    "numpy",                   # Too loose, may break with updates
]
```


## 2. Organize Optional Dependencies


```toml
[project.optional-dependencies]
# Group by purpose
dev = ["pytest", "ruff", "mypy"]
docs = ["mkdocs", "mkdocs-material"]
viz = ["plotly", "matplotlib"]

# Convenience groups
test = ["pytest", "pytest-cov"]
lint = ["ruff", "mypy"]
all = ["my-project[dev,docs,viz]"]
```


## 3. Use src Layout


```
my-project/
├── pyproject.toml
├── src/
│   └── my_project/
│       ├── __init__.py
│       └── core.py
└── tests/
    └── test_core.py
```


## 4. Keep Tools Consistent


```toml
# Use same line-length everywhere
[tool.ruff]
line-length = 88

[tool.black]
line-length = 88

[tool.isort]
line_length = 88
```
