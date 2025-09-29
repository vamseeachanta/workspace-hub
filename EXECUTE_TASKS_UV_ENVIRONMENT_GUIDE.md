# 📦 Execute Tasks - UV Environment Guidelines

## 🚨 CRITICAL REQUIREMENT

**MANDATORY**: The `/execute-tasks` and `/execute-tasks-enhanced` commands MUST use the existing repository's `uv` environment. Never create new virtual environments.

## Overview

All task execution must respect and utilize the repository's existing Python environment setup. This ensures consistency, prevents dependency conflicts, and maintains reproducible builds across all development and CI/CD pipelines.

## UV Environment Detection

The execute-tasks commands automatically detect and use:

### 1. **UV Virtual Environment**
```bash
# Standard uv environment locations
.venv/          # Default uv venv location
venv/           # Alternative location
.python-version # Python version specification
```

### 2. **Dependency Management Files**
```bash
uv.lock              # UV lock file (highest priority)
pyproject.toml       # Project configuration
requirements.txt     # Traditional requirements
requirements-dev.txt # Development dependencies
```

## Proper Library Installation

### ✅ CORRECT Installation Methods

```bash
# Using uv (PREFERRED)
uv pip install pytest-xdist
uv pip install -r requirements.txt
uv pip sync uv.lock

# In activated venv (if uv not available)
source .venv/bin/activate
pip install pytest-xdist
```

### ❌ INCORRECT Installation Methods

```bash
# NEVER do these:
pip install pytest-xdist          # Global installation
python -m venv new_env            # Creating new environment
conda create -n myenv             # Creating conda environment
pipenv install                    # Different environment manager
poetry install                    # Unless repo uses Poetry
```

## Repository Guidelines Hierarchy

Follow this priority order for dependency management:

1. **uv.lock** - If exists, use `uv pip sync uv.lock`
2. **pyproject.toml** - Check [project.dependencies] section
3. **requirements.txt** - Use `uv pip install -r requirements.txt`
4. **setup.py** - Legacy, use `uv pip install -e .`
5. **Pipfile.lock** - Convert to uv if needed

## Environment Verification

### Check Current Environment

```bash
# Verify uv environment is active
which python
# Should show: /path/to/repo/.venv/bin/python

# Check uv version
uv --version

# List installed packages
uv pip list
```

### Environment Info Display

When running `/execute-tasks-enhanced`, you'll see:

```
🔧 REPOSITORY ENVIRONMENT
============================================================
✅ UV environment detected
   Location: .venv/
🐍 Python version: 3.11.5
📦 Dependencies: pyproject.toml
📥 Install command: uv pip sync uv.lock

📝 IMPORTANT GUIDELINES:
   • ALWAYS use the existing repo environment
   • NEVER create new virtual environments
   • Follow repo's dependency management
   • Use 'uv pip install' for new packages
   • Check pyproject.toml or requirements.txt first
============================================================
```

## Common Scenarios

### Scenario 1: Installing Test Dependencies

```bash
# Check if pytest-xdist is needed for parallel testing
uv pip show pytest-xdist

# If not installed, add to repo dependencies
echo "pytest-xdist>=3.0.0" >> requirements-dev.txt
uv pip install -r requirements-dev.txt

# Or add to pyproject.toml
[project.optional-dependencies]
dev = ["pytest-xdist>=3.0.0"]
```

### Scenario 2: Missing Dependencies During Execution

```bash
# Error: ModuleNotFoundError: No module named 'xyz'

# CORRECT approach:
# 1. Check if it should be in repo dependencies
grep -r "xyz" pyproject.toml requirements*.txt

# 2. Add to appropriate file
echo "xyz>=1.0.0" >> requirements.txt

# 3. Install using uv
uv pip install -r requirements.txt

# 4. Commit the change
git add requirements.txt
git commit -m "Add xyz dependency for task execution"
```

### Scenario 3: Conflicting Dependencies

```bash
# If uv pip install fails due to conflicts

# 1. Check current constraints
uv pip list --format=freeze > current.txt

# 2. Identify conflicts
uv pip check

# 3. Resolve in pyproject.toml or requirements.txt
# Specify compatible versions

# 4. Regenerate lock file
uv pip compile pyproject.toml -o uv.lock
```

## Task Execution Commands

### Standard Execution
```bash
# Uses repo's uv environment automatically
/execute-tasks @.agent-os/specs/feature/tasks.md

# The command internally uses:
uv run python -m pytest           # For tests
uv run python script.py           # For scripts
```

### Enhanced Execution with Parallel Processing
```bash
# Automatically detects and uses uv environment
/execute-tasks-enhanced tasks.md --workers 10

# Internally runs tests with:
uv run python -m pytest -n auto   # Parallel testing
```

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Setup UV
  uses: astral-sh/setup-uv@v2
  with:
    version: 'latest'

- name: Install dependencies
  run: |
    uv venv
    uv pip sync uv.lock

- name: Execute tasks
  run: |
    uv run /execute-tasks-enhanced tasks.md
```

### Docker Example
```dockerfile
FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Create venv and install dependencies
RUN uv venv && uv pip sync uv.lock

# Execute tasks using uv environment
CMD ["uv", "run", "/execute-tasks", "tasks.md"]
```

## Best Practices

### 1. **Never Mix Environment Managers**
- Don't use pip, pipenv, poetry, and uv in the same project
- Stick to the repo's chosen tool (preferably uv)

### 2. **Document Dependencies**
```toml
# pyproject.toml
[project]
dependencies = [
    "pytest>=7.0.0",
    "requests>=2.28.0",
]

[project.optional-dependencies]
dev = [
    "pytest-xdist>=3.0.0",
    "black>=23.0.0",
]
```

### 3. **Lock Dependencies**
```bash
# Generate lock file for reproducible builds
uv pip compile pyproject.toml -o uv.lock

# Commit both files
git add pyproject.toml uv.lock
git commit -m "Lock dependencies"
```

### 4. **Test in Clean Environment**
```bash
# Verify dependencies work in fresh environment
rm -rf .venv
uv venv
uv pip sync uv.lock
uv run pytest
```

## Troubleshooting

### Issue: Command Not Using UV Environment

**Solution:**
```bash
# Explicitly activate environment
source .venv/bin/activate

# Or use uv run prefix
uv run /execute-tasks tasks.md
```

### Issue: Missing uv Command

**Solution:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip
pip install uv
```

### Issue: Dependencies Not Found

**Solution:**
```bash
# Ensure uv.lock is up to date
uv pip compile pyproject.toml -o uv.lock

# Sync dependencies
uv pip sync uv.lock
```

### Issue: Python Version Mismatch

**Solution:**
```bash
# Check required version
cat .python-version

# Install correct version
uv python install 3.11.5

# Recreate venv
rm -rf .venv
uv venv --python 3.11.5
```

## Repository Integration Checklist

When setting up `/execute-tasks` in a new repository:

- [ ] Check for existing `.venv/` or `venv/` directory
- [ ] Verify `.python-version` file exists
- [ ] Ensure `pyproject.toml` or `requirements.txt` present
- [ ] Install uv if not available: `pip install uv`
- [ ] Create venv if needed: `uv venv`
- [ ] Install dependencies: `uv pip sync uv.lock`
- [ ] Test execution: `uv run /execute-tasks --help`
- [ ] Document in README: "Uses uv for dependency management"
- [ ] Add to `.gitignore`: `.venv/` and `__pycache__/`
- [ ] Commit `uv.lock` for reproducible builds

## Summary

**Key Points:**
- ✅ ALWAYS use existing repo's uv environment
- ✅ Install libraries with `uv pip install`
- ✅ Follow repo's dependency files (uv.lock, pyproject.toml)
- ❌ NEVER create new virtual environments
- ❌ NEVER use global Python installations
- ❌ NEVER mix environment managers

**The `/execute-tasks` commands are designed to seamlessly integrate with your repository's existing uv environment setup, ensuring consistent and reliable task execution.**

---

*This is MANDATORY for all task execution commands across all repositories.*