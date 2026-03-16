---
name: pyproject-toml
version: 1.0.0
description: Configure Python projects with pyproject.toml for modern packaging, tools,
  and dependency management
author: workspace-hub
category: development
tags:
- python
- pyproject
- configuration
- packaging
- build-system
platforms:
- python
capabilities: []
requires: []
see_also:
- pyproject-toml-complete-pyprojecttoml-template
- pyproject-toml-1-build-system
- pyproject-toml-pytest
- pyproject-toml-example-1-data-processing-library
---

# Pyproject Toml

## When to Use This Skill

Use pyproject.toml configuration when you need:
- **Project metadata** - Name, version, description, authors
- **Dependency management** - Core and optional dependencies
- **Build configuration** - Setuptools, hatch, flit, or poetry
- **Tool configuration** - pytest, ruff, mypy, black, isort
- **Entry points** - CLI scripts and plugins
- **Package discovery** - Source directory configuration

**Avoid when:**
- Legacy projects requiring setup.py (rare, migrate instead)
- Non-Python projects

## Resources

- **PEP 517**: Build system interface
- **PEP 518**: pyproject.toml specification
- **PEP 621**: Project metadata
- **PEP 660**: Editable installs
- **Setuptools**: https://setuptools.pypa.io/
- **UV**: https://docs.astral.sh/uv/

---

**Use this template for all Python projects in workspace-hub!**

## Sub-Skills

- [1. Version Constraints (+3)](1-version-constraints/SKILL.md)

## Sub-Skills

- [Complete pyproject.toml Template](complete-pyprojecttoml-template/SKILL.md)
- [1. Build System (+4)](1-build-system/SKILL.md)
- [pytest (+2)](pytest/SKILL.md)
- [Example 1: Data Processing Library (+2)](example-1-data-processing-library/SKILL.md)
