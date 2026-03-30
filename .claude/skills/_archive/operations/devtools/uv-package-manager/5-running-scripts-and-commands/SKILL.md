---
name: ops-uv-package-manager-5-running-scripts-and-commands
description: 'Sub-skill of ops-uv-package-manager: 5. Running Scripts and Commands
  (+1).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 5. Running Scripts and Commands (+1)

## 5. Running Scripts and Commands


**Run Python scripts:**
```bash
# Run script with project dependencies
uv run python script.py

# Run module
uv run python -m pytest

# Run with specific Python version
uv run --python 3.11 python script.py
```

**Run tools:**
```bash
# Run pytest
uv run pytest tests/

# Run ruff for linting
uv run ruff check src/

# Run black for formatting
uv run black src/

# Run any CLI tool
uv run mypy src/
```


## 6. pip Compatibility Mode


**Use UV as a pip replacement:**
```bash
# Install packages (pip syntax)
uv pip install pandas numpy

# Install from requirements.txt
uv pip install -r requirements.txt

# Install in editable mode
uv pip install -e .

# Compile requirements
uv pip compile requirements.in -o requirements.txt

# Sync environment
uv pip sync requirements.txt

# Freeze installed packages
uv pip freeze > requirements.txt

# Show package info
uv pip show pandas
```
