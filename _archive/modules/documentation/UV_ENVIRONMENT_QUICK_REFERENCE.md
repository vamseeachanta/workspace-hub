# 🚀 UV Environment Quick Reference

## 🔴 CRITICAL: Task Execution Rules

**MANDATORY for `/execute-tasks` and `/execute-tasks-enhanced`:**

### ✅ ALWAYS DO THIS
```bash
# Use existing repo environment
uv pip install <package>         # Install new packages
uv pip sync uv.lock              # Sync dependencies
uv run python script.py          # Run Python scripts
uv run pytest                    # Run tests
source .venv/bin/activate        # Activate if needed
```

### ❌ NEVER DO THIS
```bash
# These will break repo consistency
pip install <package>            # Global install
python -m venv new_env          # New environment
conda create -n myenv           # Different manager
pipenv install                  # Different system
poetry add <package>            # Unless repo uses Poetry
sudo pip install                # System-wide install
```

## 📁 Repository Structure

```
repo/
├── .venv/                 # UV virtual environment (DO NOT DELETE)
├── .python-version        # Python version spec (DO NOT MODIFY)
├── uv.lock               # Locked dependencies (DO NOT EDIT MANUALLY)
├── pyproject.toml        # Project config (EDIT WITH CARE)
├── requirements.txt      # Legacy deps (USE UV INSTEAD)
└── .agent-os/
    └── commands/
        └── execute-tasks-enhanced.py  # Uses repo's uv env
```

## 🎯 Common Commands

### Setup (Only if Missing)
```bash
uv venv                          # Create .venv
uv pip sync uv.lock             # Install all deps
```

### Daily Use
```bash
uv pip list                     # Show installed packages
uv pip show pytest              # Check specific package
uv run /execute-tasks tasks.md  # Run with uv env
```

### Adding Dependencies
```bash
# Add to pyproject.toml first, then:
uv pip install package-name
uv pip compile pyproject.toml -o uv.lock
git add pyproject.toml uv.lock
git commit -m "Add package-name dependency"
```

## 🔍 Quick Checks

```bash
# Am I using the right Python?
which python
# ✅ Should show: /path/to/repo/.venv/bin/python
# ❌ Not: /usr/bin/python or /usr/local/bin/python

# Is uv environment active?
echo $VIRTUAL_ENV
# ✅ Should show: /path/to/repo/.venv
# ❌ Not: empty or different path

# Are dependencies installed?
uv pip list | grep pytest
# ✅ Should list pytest and version
# ❌ Not: command not found or empty
```

## 🚨 Emergency Fixes

### "Module not found" Error
```bash
uv pip sync uv.lock              # Reinstall all deps
```

### Wrong Python Version
```bash
cat .python-version              # Check required
uv python install 3.11.5         # Install correct
uv venv --python 3.11.5         # Recreate venv
```

### Dependency Conflicts
```bash
uv pip check                     # Find conflicts
uv pip compile pyproject.toml -o uv.lock  # Resolve
```

## 📋 Task Execution Checklist

Before running `/execute-tasks`:
- [ ] ✅ In repository root directory
- [ ] ✅ `.venv/` directory exists
- [ ] ✅ `uv.lock` file present
- [ ] ✅ Dependencies synced: `uv pip sync uv.lock`
- [ ] ✅ Using repo's Python: `which python` shows `.venv/bin/python`

## 💡 Remember

> **The `/execute-tasks` commands automatically detect and use your repo's uv environment. You don't need to activate it manually, but you MUST have it properly set up.**

---

**Golden Rule**: If you're about to type `pip install`, stop and use `uv pip install` instead!