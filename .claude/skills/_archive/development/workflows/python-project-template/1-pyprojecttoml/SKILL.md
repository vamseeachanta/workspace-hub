---
name: python-project-template-1-pyprojecttoml
description: 'Sub-skill of python-project-template: 1. pyproject.toml (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. pyproject.toml (+2)

## 1. pyproject.toml


```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{{project_name}}"
version = "0.1.0"
description = "{{description}}"
readme = "README.md"

*See sub-skills for full details.*

## 2. conftest.py


```python
"""
ABOUTME: Pytest configuration and fixtures for {{project_name}}
ABOUTME: Provides shared fixtures and test utilities
"""

import sys
from pathlib import Path

import pytest

*See sub-skills for full details.*

## 3. CLAUDE.md Template


```markdown
# Claude Code - {{project_name}}

> AI agent instructions for {{project_name}}
