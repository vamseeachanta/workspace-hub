---
name: python-project-template-key-commands
description: 'Sub-skill of python-project-template: Key Commands.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Key Commands

## Key Commands


```bash
# Setup environment
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src tests
ruff check src tests --fix

# Type check
mypy src
```
