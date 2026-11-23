---
name: python-project-template
description: Generate standardized Python project structure with pyproject.toml, UV
  environment, pytest configuration, and workspace-hub compliance. Creates production-ready
  project scaffolding.
version: 1.0.0
category: development
type: skill
trigger: manual
auto_execute: false
capabilities:
- project_scaffolding
- pyproject_generation
- dependency_configuration
- testing_setup
- uv_environment
tools:
- Write
- Bash
- Read
related_skills:
- pytest-fixture-generator
requires: []
tags: []
---

# Python Project Template

## Quick Start

```bash
# Create new project
/python-project-template my-project

# Create with specific type
/python-project-template my-project --type library

# Create in specific directory
/python-project-template my-project --path /path/to/projects
```

## When to Use

**USE when:**
- Starting a new Python project
- Adding a new repository to workspace-hub
- Standardizing an existing project
- Creating reusable modules

**DON'T USE when:**
- Project already has proper structure
- Non-Python projects
- One-off scripts (use scripts/ directory instead)

## Prerequisites

- Python 3.9+
- UV package manager installed
- Git initialized in parent directory

## Overview

Creates a complete Python project with:

1. **pyproject.toml** - Modern Python packaging configuration
2. **UV environment** - Fast dependency management
3. **Test structure** - pytest with fixtures and coverage
4. **Source layout** - Modular src/ organization
5. **Documentation** - README, CLAUDE.md, .agent-os/
6. **Quality tools** - ruff, black, mypy configuration

## Related Skills

- [pytest-fixture-generator](../pytest-fixture-generator/SKILL.md) - Enhanced testing
- [repo-readiness](../repo-readiness/SKILL.md) - Verify project setup
- [agent-os-framework](../agent-os-framework/SKILL.md) - Full product documentation

## References

- [Python Packaging Guide](https://packaging.python.org/)
- [UV Documentation](https://github.com/astral-sh/uv)
- [workspace-hub Standards](../../../docs/modules/standards/)

---

## Version History

- **1.0.0** (2026-01-14): Initial release - standardized Python project generation with pyproject.toml, UV support, pytest configuration, and workspace-hub compliance

## Sub-Skills

- [Example 1: Create Basic Project (+2)](example-1-create-basic-project/SKILL.md)
- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [Project Structure Generated](project-structure-generated/SKILL.md)
- [1. pyproject.toml (+2)](1-pyprojecttoml/SKILL.md)
- [Project Overview](project-overview/SKILL.md)
- [Critical Rules](critical-rules/SKILL.md)
- [File Organization](file-organization/SKILL.md)
- [Key Commands](key-commands/SKILL.md)
- [4. Core Module Template](4-core-module-template/SKILL.md)
- [With repo-readiness (+1)](with-repo-readiness/SKILL.md)
