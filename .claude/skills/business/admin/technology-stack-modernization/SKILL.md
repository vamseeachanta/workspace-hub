---
capabilities: []
requires: []
see_also: []
---

# Technology Stack Modernization Skill

> Version: 1.0.0
> Created: 2026-01-08
> Category: Technical Architecture, Dependency Management, Standards Compliance

## Overview

This skill provides a systematic approach to modernizing technology stacks in existing projects, including updating dependencies, replacing deprecated packages, adopting modern Python features, and ensuring workspace-hub standards compliance.

## When to Use

Use this skill when:
- Updating dependencies to current stable versions
- Replacing deprecated packages with modern alternatives
- Migrating from legacy tools (Conda → UV, PyPDF2 → pypdf, Matplotlib → Plotly)
- Adopting modern Python features (3.11+ type hints, performance improvements)
- Ensuring workspace-hub standards compliance (UV, Plotly, file organization)
- Modernizing development tools (Ruff instead of Black+isort+flake8)
- Documenting technology choices and rationale

## Skill Components

### 1. Dependency Version Assessment

**Process:**
1. Identify current dependency versions in project
2. Check for available updates on PyPI
3. Review CHANGELOG for breaking changes
4. Test compatibility with existing code
5. Update pyproject.toml with version constraints

**Version Update Checklist:**
```markdown
### Current Dependencies Review

| Package | Current | Latest | Breaking Changes? | Action |
|---------|---------|--------|-------------------|--------|
| pandas | 1.5.3 | 2.2.0 | Yes - deprecated methods | Update + refactor |
| numpy | 1.24.0 | 1.26.0 | No | Safe update |
| plotly | 5.14.0 | 5.18.0 | No | Safe update |
| click | 8.1.0 | 8.1.7 | No | Safe update |

### Update Strategy
1. **Safe updates** (no breaking changes): Batch update
2. **Breaking changes**: Update one at a time with testing
3. **Major versions**: Review migration guides first
4. **Test after each update**: Run full test suite
```

### 2. Deprecated Package Replacement

**Common Replacements:**

**Conda → UV (Package Manager)**
```bash
# Before (Conda)
conda create -n myenv python=3.11
conda activate myenv
conda install pandas numpy plotly

# After (UV) - workspace-hub standard
uv venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
uv pip install -e .
```

**PyPDF2 → pypdf (PDF Processing)**
```python
# Before (PyPDF2 - deprecated)
from PyPDF2 import PdfReader, PdfWriter

reader = PdfReader('input.pdf')
writer = PdfWriter()

# After (pypdf - modern)
from pypdf import PdfReader, PdfWriter

reader = PdfReader('input.pdf')
writer = PdfWriter()
```

**Matplotlib → Plotly (Visualizations)**
```python
# Before (Matplotlib - static, workspace-hub violation)
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('data.csv')
plt.scatter(df['x'], df['y'])
plt.savefig('plot.png')

# After (Plotly - interactive, workspace-hub standard)
import plotly.express as px
import pandas as pd

df = pd.read_csv('../data/processed/data.csv')  # Relative path
fig = px.scatter(df, x='x', y='y', title='Interactive Plot')
fig.write_html('../reports/plot.html')  # Interactive HTML
```

**Black + isort + flake8 → Ruff (Linting)**
```toml
# Before (pyproject.toml)
[tool.black]
line-length = 100

[tool.isort]
profile = "black"

# After (Ruff - all-in-one)
[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "I"]
```

### 3. Modern Python Features Adoption

**Python 3.11+ Features:**

**Type Hints and Generics**
```python
# Before (Python 3.9)
from typing import List, Dict, Optional

def process_data(items: List[str]) -> Dict[str, int]:
    result: Dict[str, int] = {}
    for item in items:
        result[item] = len(item)
    return result

# After (Python 3.11+)
def process_data(items: list[str]) -> dict[str, int]:
    result: dict[str, int] = {}
    for item in items:
        result[item] = len(item)
    return result
```

**Exception Groups**
```python
# Python 3.11+ - Multiple exception handling
try:
    process_multiple_files(files)
except* FileNotFoundError as e:
    log.error(f"Missing files: {e.exceptions}")
except* PermissionError as e:
    log.error(f"Permission denied: {e.exceptions}")
```

**Performance Improvements**
```python
# Python 3.11+ - Faster imports, execution
# Just upgrade Python version, no code changes needed
# Typical speedup: 10-25% faster execution
```

### 4. pyproject.toml Modernization

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
    "numpy>=1.24.0",

    # Visualization (interactive only)
    "plotly>=5.14.0",
    "kaleido>=0.2.1",

    # Document Processing (modern alternatives)
    "pypdf>=3.0.0",           # NOT PyPDF2
    "python-docx>=1.0.0",

    # CLI Development
    "click>=8.1.0",
    "rich>=13.4.0",

    # Configuration
    "pyyaml>=6.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    # Testing
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.11.0",

    # Code Quality (Ruff instead of Black+isort+flake8)
    "ruff>=0.1.0",
    "mypy>=1.5.0",
    "pre-commit>=3.3.0",
]

[project.scripts]
main-command = "package.module:main"

[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "--cov=src --cov-report=html --cov-report=term"

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/venv/*"]

[tool.coverage.report]
precision = 2
show_missing = true
fail_under = 80.0

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### 5. Development Tools Update

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

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

**VS Code Settings Update:**
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": true,
      "source.organizeImports": true
    }
  },
  "ruff.args": ["--config=pyproject.toml"]
}
```

## Templates

### Tech Stack Migration Checklist

```markdown
# Technology Stack Modernization Checklist

## Phase 1: Assessment
- [ ] Document current dependencies and versions
- [ ] Identify deprecated packages
- [ ] Check for workspace-hub violations (Conda, Matplotlib, root files)
- [ ] Review Python version (must be 3.11+)
- [ ] Assess breaking changes in major updates

## Phase 2: Package Manager Migration
- [ ] Replace Conda/Poetry with UV
- [ ] Create pyproject.toml with project metadata
- [ ] Configure uv venv setup
- [ ] Update README with UV installation instructions
- [ ] Remove conda.yaml, environment.yml, poetry.lock

## Phase 3: Dependency Updates
- [ ] Update Pandas to 2.0+ (check for deprecated methods)
- [ ] Update NumPy to 1.24+ (ensure compatibility)
- [ ] Replace PyPDF2 with pypdf
- [ ] Update all other dependencies to current stable versions
- [ ] Test after each major update

## Phase 4: Visualization Migration
- [ ] Replace all Matplotlib with Plotly
- [ ] Convert static plots to interactive HTML
- [ ] Update data paths to relative paths
- [ ] Move all visualizations to /reports/ directory
- [ ] Remove matplotlib, seaborn dependencies

## Phase 5: Development Tools
- [ ] Replace Black+isort+flake8 with Ruff
- [ ] Configure pre-commit hooks
- [ ] Update VS Code settings for Ruff
- [ ] Set up mypy for type checking
- [ ] Configure pytest with coverage

## Phase 6: Modern Python Features
- [ ] Update type hints to use built-in types (list, dict vs List, Dict)
- [ ] Adopt Python 3.11+ features where beneficial
- [ ] Update f-strings and error handling
- [ ] Remove Python 3.9 compatibility workarounds

## Phase 7: Testing & Validation
- [ ] Run full test suite
- [ ] Verify all CLI commands work
- [ ] Check visualization outputs
- [ ] Validate workspace-hub compliance
- [ ] Update documentation

## Phase 8: Documentation
- [ ] Update tech-stack.md with current versions
- [ ] Document rationale for technology choices
- [ ] Update README with setup instructions
- [ ] Add migration notes for future reference
```

### Dependency Update Template

```markdown
## Dependency: [Package Name]

### Current State
- **Version:** [current_version]
- **Usage:** [where/how it's used]
- **Issues:** [any known problems]

### Update Plan
- **Target Version:** [target_version]
- **Breaking Changes:** [yes/no - list if yes]
- **Migration Steps:**
  1. [step 1]
  2. [step 2]
  3. [step 3]

### Testing Plan
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Performance benchmarks within acceptable range

### Rollback Plan
If update fails:
1. Revert pyproject.toml changes
2. Reinstall previous version: `uv pip install [package]==[old_version]`
3. Document issue for future reference
```

## Examples

### Example 1: Complete Tech Stack Modernization

**Before (tech-stack.md):**
```markdown
### Python Environment
- **Python 3.9+**
- **Conda** - Package and environment management
- **pip** - Python package installer

### Dependencies
- Pandas 1.5.0
- NumPy 1.23.0
- Matplotlib 3.6.0
- PyPDF2 3.0.0

### Development Tools
- Black - Code formatting
- isort - Import sorting
- flake8 - Linting
```

**After (tech-stack.md):**
```markdown
### Python Environment
- **Python 3.11+** - Modern type hints and 10-25% performance improvement
- **UV Package Manager** - Fast, reliable package and environment management (workspace-hub standard)

### Dependencies
- **pandas>=2.0.0** - Data processing with improved performance
- **numpy>=1.24.0** - Numerical computing
- **plotly>=5.14.0** - Interactive visualizations (MANDATORY - workspace-hub standard)
- **pypdf>=3.0.0** - Modern PDF processing (replaces deprecated PyPDF2)

**Note:** All visualizations MUST be interactive (Plotly). No static matplotlib charts per workspace-hub standards.

### Development Tools
- **Ruff** - All-in-one linter, formatter, and import sorter (replaces Black+isort+flake8)
- **mypy** - Static type checking
- **pytest** - Testing framework with coverage reporting
```

**pyproject.toml Changes:**
```toml
# Before
[build-system]
requires = ["setuptools", "wheel"]

# After
[project]
name = "project-name"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "plotly>=5.14.0",
    "pypdf>=3.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]

[tool.ruff]
line-length = 100
target-version = "py311"
```

### Example 2: Matplotlib → Plotly Migration

**Before:**
```python
# src/analysis/visualizer.py
import matplotlib.pyplot as plt
import pandas as pd

def create_scatter_plot(data_path: str, output_path: str):
    """Create scatter plot of analysis results."""
    df = pd.read_csv(data_path)

    plt.figure(figsize=(10, 6))
    plt.scatter(df['x'], df['y'], alpha=0.5)
    plt.xlabel('X Values')
    plt.ylabel('Y Values')
    plt.title('Analysis Results')
    plt.grid(True)
    plt.savefig(output_path, dpi=300)
    plt.close()
```

**After:**
```python
# src/analysis/visualizer.py
import plotly.express as px
import pandas as pd
from pathlib import Path

def create_scatter_plot(data_path: str, output_path: str):
    """Create interactive scatter plot of analysis results."""
    # Use relative path from report location
    df = pd.read_csv(f"../{data_path}")

    # Create interactive Plotly chart
    fig = px.scatter(
        df,
        x='x',
        y='y',
        title='Analysis Results',
        labels={'x': 'X Values', 'y': 'Y Values'},
        hover_data=['x', 'y']  # Show values on hover
    )

    # Customize layout
    fig.update_layout(
        template='plotly_white',
        hovermode='closest',
        height=600
    )

    # Save as interactive HTML
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(output_path, include_plotlyjs='cdn')
```

**Benefits:**
- Interactive hover tooltips (show exact values)
- Zoom and pan capabilities
- Export options (PNG, SVG) built-in
- Responsive design (mobile-friendly)
- No separate image files needed
- Workspace-hub compliant

## Best Practices

### Dependency Management
1. **Pin major versions, allow minor updates:**
   ```toml
   # Good: Allows security updates
   dependencies = ["pandas>=2.0.0,<3.0.0"]

   # Bad: Too strict, misses security patches
   dependencies = ["pandas==2.0.0"]
   ```

2. **Test after each major update:**
   - Update one package at a time
   - Run full test suite
   - Check for deprecation warnings
   - Validate outputs

3. **Document breaking changes:**
   ```markdown
   ## Pandas 1.5 → 2.0 Migration Notes

   **Breaking Changes:**
   - `DataFrame.append()` removed → use `pd.concat()`
   - `Series.append()` removed → use `pd.concat()`

   **Migration:**
   ```python
   # Before
   df = df.append(new_rows)

   # After
   df = pd.concat([df, new_rows], ignore_index=True)
   ```
   ```

### Workspace-Hub Compliance
1. **Always use UV, never Conda/Poetry**
2. **Always use Plotly, never Matplotlib/Seaborn**
3. **Always use relative paths for CSV data**
4. **Always organize files in directories, never root**
5. **Always use modern Python (3.11+)**

### Migration Safety
1. **Create feature branch for updates:**
   ```bash
   git checkout -b tech-stack-modernization
   ```

2. **Commit frequently with clear messages:**
   ```bash
   git commit -m "Update pandas 1.5 → 2.0 (breaking changes addressed)"
   git commit -m "Replace matplotlib with plotly (workspace-hub compliance)"
   ```

3. **Keep rollback option available:**
   ```bash
   # Tag before major changes
   git tag v1.0.0-pre-modernization
   ```

### Performance Considerations
1. **Python 3.11+ gives 10-25% speed boost** (no code changes)
2. **UV is 10-100x faster** than pip for environment setup
3. **Plotly HTML can be large** - use CDN mode: `include_plotlyjs='cdn'`
4. **Ruff is 10-100x faster** than Black+isort+flake8 combined

## Related Skills

- **Product Documentation Modernization** - For updating mission.md and tech-stack.md
- **Workspace-Hub Standards Compliance** - For verification and validation
- **Quantification & Metrics** - For calculating modernization ROI

## References

### Official Documentation
- [UV Documentation](https://github.com/astral-sh/uv)
- [Plotly Python](https://plotly.com/python/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Python 3.11 Release Notes](https://docs.python.org/3/whatsnew/3.11.html)
- [PyPI - pypdf](https://pypi.org/project/pypdf/)

### Migration Guides
- [Pandas 2.0 Migration Guide](https://pandas.pydata.org/docs/whatsnew/v2.0.0.html)
- [PyPDF2 to pypdf Migration](https://pypdf.readthedocs.io/en/stable/user/migration-1-to-2.html)
- [Matplotlib to Plotly Conversion](https://plotly.com/python/matplotlib-to-plotly/)

### Workspace-Hub Standards
- FILE_ORGANIZATION_STANDARDS.md
- HTML_REPORTING_STANDARDS.md
- LOGGING_STANDARDS.md

## Success Criteria

✅ **Modernization Complete When:**
- [ ] Python version is 3.11+
- [ ] UV package manager configured (no Conda/Poetry)
- [ ] All dependencies at current stable versions
- [ ] PyPDF2 replaced with pypdf
- [ ] Matplotlib replaced with Plotly (all charts interactive)
- [ ] Ruff configured (replaces Black+isort+flake8)
- [ ] pyproject.toml complete with all sections
- [ ] Pre-commit hooks configured
- [ ] Full test suite passes
- [ ] Documentation updated
- [ ] Workspace-hub compliance verified

---

## Version History

- **1.0.0** (2026-01-08): Initial release - comprehensive technology stack modernization skill
