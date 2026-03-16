---
name: technology-stack-modernization-1-dependency-version-assessment
description: 'Sub-skill of technology-stack-modernization: 1. Dependency Version Assessment
  (+6).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 1. Dependency Version Assessment (+6)

## 1. Dependency Version Assessment


**Process:**
1. Identify current dependency versions in project
2. Check for available updates on PyPI
3. Review CHANGELOG for breaking changes
4. Test compatibility with existing code
5. Update pyproject.toml with version constraints

**Version Update Checklist:**
```markdown

## Current Dependencies Review


| Package | Current | Latest | Breaking Changes? | Action |
|---------|---------|--------|-------------------|--------|
| pandas | 1.5.3 | 2.2.0 | Yes - deprecated methods | Update + refactor |
| numpy | 1.24.0 | 1.26.0 | No | Safe update |
| plotly | 5.14.0 | 5.18.0 | No | Safe update |
| click | 8.1.0 | 8.1.7 | No | Safe update |

## Update Strategy


1. **Safe updates** (no breaking changes): Batch update
2. **Breaking changes**: Update one at a time with testing
3. **Major versions**: Review migration guides first
4. **Test after each update**: Run full test suite
```

## 2. Deprecated Package Replacement


**Common Replacements:**

**Conda → UV (Package Manager)**
```bash
# Before (Conda)
conda create -n myenv python=3.11
conda activate myenv
conda install pandas numpy plotly

# After (UV) - workspace-hub standard

*See sub-skills for full details.*

## 3. Modern Python Features Adoption


**Python 3.11+ Features:**

**Type Hints and Generics**
```python
# Before (Python 3.9)
from typing import List, Dict, Optional

def process_data(items: List[str]) -> Dict[str, int]:
    result: Dict[str, int] = {}
    for item in items:

*See sub-skills for full details.*

## 4. pyproject.toml Modernization


**Complete Modern Configuration:**
```toml
[project]
name = "project-name"
version = "1.0.0"
description = "Project description"
requires-python = ">=3.11"
dependencies = [
    # Data Processing (current versions)
    "pandas>=2.0.0",

*See sub-skills for full details.*

## 5. Development Tools Update


**Pre-commit Hooks Configuration:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

*See sub-skills for full details.*
